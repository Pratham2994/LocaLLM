"""Load machine files, sampling presets and experiment configs (all YAML)."""

import hashlib
import json
import socket
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "configs"
MACHINE_DIR = CONFIG_DIR / "machines"
PRESET_FILE = CONFIG_DIR / "presets" / "sampling.yaml"

REQUIRED_SAMPLING = {"temperature", "top_p", "top_k", "min_p", "presence_penalty"}
OPTIONAL_SAMPLING = {"frequency_penalty", "repeat_penalty"}


class ConfigError(ValueError):
    pass


def read_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ConfigError(f"{path}: expected a YAML mapping at the top level")
    return data


def check_keys(where: str, data: dict, required: set[str], optional: set[str]) -> None:
    """Fail on missing keys and on unknown keys (a typo must not be silently ignored)."""
    missing = required - data.keys()
    unknown = data.keys() - required - optional
    if missing:
        raise ConfigError(f"{where}: missing keys {sorted(missing)}")
    if unknown:
        raise ConfigError(f"{where}: unknown keys {sorted(unknown)} (typo?)")


@dataclass(frozen=True)
class Backend:
    name: str
    dir: Path
    threads: int
    args: tuple[str, ...]

    @property
    def server_exe(self) -> Path:
        for name in ("llama-server.exe", "llama-server"):
            if (self.dir / name).exists():
                return self.dir / name
        raise ConfigError(f"no llama-server executable in {self.dir}")


@dataclass(frozen=True)
class Machine:
    name: str
    host: str
    port: int
    model_dirs: tuple[Path, ...]
    backends: dict[str, Backend]
    tools: dict[str, str]
    health_timeout_s: float

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


def load_machine(name: str | None = None) -> Machine:
    """Load configs/machines/<name>.yaml, or the file whose `hostname` matches this computer."""
    files = sorted(MACHINE_DIR.glob("*.yaml"))
    if name:
        path = MACHINE_DIR / f"{name}.yaml"
        if not path.exists():
            raise ConfigError(f"no machine file {path}")
    else:
        host = socket.gethostname().casefold()
        matches = [p for p in files if str(read_yaml(p).get("hostname", "")).casefold() == host]
        if len(matches) == 1:
            path = matches[0]
        else:
            raise ConfigError(
                f"no single machine file in {MACHINE_DIR} has hostname {socket.gethostname()!r}; "
                "add one or pass --machine"
            )
    data = read_yaml(path)
    check_keys(str(path), data, {"hostname", "backends", "model_dirs"},
               {"host", "port", "tools", "health_timeout_s", "notes"})
    backends = {}
    for bname, b in data["backends"].items():
        check_keys(f"{path}: backends.{bname}", b, {"dir", "threads"}, {"args", "notes"})
        backends[bname] = Backend(bname, Path(b["dir"]), int(b["threads"]),
                                  tuple(str(a) for a in b.get("args") or []))
    tools = {"python": sys.executable, "node": "node", "cxx": "g++"} | dict(data.get("tools") or {})
    return Machine(
        name=path.stem,
        host=str(data.get("host", "127.0.0.1")),
        port=int(data.get("port", 8080)),
        model_dirs=tuple(Path(d) for d in data["model_dirs"]),
        backends=backends,
        tools=tools,
        health_timeout_s=float(data.get("health_timeout_s", 300)),
    )


@dataclass(frozen=True)
class RunConfig:
    name: str
    path: Path
    model: Path
    model_bytes: int
    backend: Backend
    ctx: int
    kv_cache: str
    thinking: bool
    sampling_preset: str | None
    sampling: dict
    repeats: int
    max_tokens: int
    request_timeout_s: float
    server_args: tuple[str, ...]

    def server_command(self, machine: Machine) -> list[str]:
        cmd = [
            str(self.backend.server_exe), "-m", str(self.model),
            "--host", machine.host, "--port", str(machine.port),
            "-t", str(self.backend.threads), "-np", "1", "--cache-ram", "0",
            "-c", str(self.ctx), "-lv", "4",  # -lv 4 prints the buffer sizes
            *self.backend.args,
        ]
        if self.kv_cache != "f16":
            cmd += ["-ctk", self.kv_cache, "-ctv", self.kv_cache]
        return cmd + list(self.server_args)

    @property
    def config_hash(self) -> str:
        """Changes when anything that can change a result changes. Excludes `repeats`
        (raising it should add runs, not redo them) and paths (they differ per machine)."""
        key = {
            "model": self.model.name, "model_bytes": self.model_bytes,
            "backend": self.backend.name, "threads": self.backend.threads,
            "backend_args": list(self.backend.args), "ctx": self.ctx, "kv_cache": self.kv_cache,
            "thinking": self.thinking, "sampling": self.sampling, "max_tokens": self.max_tokens,
            "server_args": list(self.server_args),
        }
        return hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()[:12]


def resolve_model(spec: str, machine: Machine) -> Path:
    path = Path(spec)
    if path.is_absolute():
        if not path.is_file():
            raise ConfigError(f"model file not found: {path}")
        return path
    hits = {
        hit.resolve()
        for d in machine.model_dirs if d.is_dir()
        for hit in d.rglob(path.name)
        if hit.is_file() and not any(part.startswith(".") for part in hit.relative_to(d).parts)
    }
    if not hits:
        raise ConfigError(f"model {spec!r} not found in {[str(d) for d in machine.model_dirs]}")
    if len(hits) > 1:
        raise ConfigError(f"model {spec!r} is ambiguous, use a full path: {sorted(map(str, hits))}")
    return hits.pop()


def resolve_sampling(spec: object, where: str) -> tuple[dict, str | None]:
    if isinstance(spec, str):
        presets = read_yaml(PRESET_FILE)
        if spec not in presets:
            raise ConfigError(f"{where}: unknown sampling preset {spec!r} (have {sorted(presets)})")
        values, preset = presets[spec], spec
    elif isinstance(spec, dict):
        values, preset = spec, None
    else:
        raise ConfigError(f"{where}: sampling must be a preset name or a mapping")
    check_keys(f"{where}: sampling", values, REQUIRED_SAMPLING, OPTIONAL_SAMPLING)
    return dict(values), preset


def load_run_config(path: Path, machine: Machine) -> RunConfig:
    data = read_yaml(path)
    check_keys(str(path), data, {"name", "model", "backend", "ctx", "thinking", "sampling"},
               {"kv_cache", "repeats", "max_tokens", "request_timeout_s", "server_args", "notes"})
    if data["backend"] not in machine.backends:
        raise ConfigError(f"{path}: backend {data['backend']!r} is not in machine "
                          f"{machine.name!r} (has {sorted(machine.backends)})")
    if not isinstance(data["thinking"], bool):
        raise ConfigError(f"{path}: thinking must be true or false")
    model = resolve_model(str(data["model"]), machine)
    sampling, preset = resolve_sampling(data["sampling"], str(path))
    return RunConfig(
        name=str(data["name"]),
        path=path,
        model=model,
        model_bytes=model.stat().st_size,
        backend=machine.backends[data["backend"]],
        ctx=int(data["ctx"]),
        kv_cache=str(data.get("kv_cache", "f16")),
        thinking=data["thinking"],
        sampling_preset=preset,
        sampling=sampling,
        repeats=int(data.get("repeats", 3)),
        max_tokens=int(data.get("max_tokens", 4096)),
        request_timeout_s=float(data.get("request_timeout_s", 1800)),
        server_args=tuple(str(a) for a in data.get("server_args") or []),
    )
