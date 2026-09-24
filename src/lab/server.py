"""Start and stop llama-server, wait until it is healthy, and parse its startup log."""

import os
import re
import socket
import subprocess
import time
from pathlib import Path

import requests

# e.g. "load_tensors:      Vulkan0 model buffer size =  2603.50 MiB"
#      "llama_kv_cache:    Vulkan0 KV buffer size =   256.00 MiB"
BUFFER_RE = re.compile(r"(\S+)\s+(model|KV|RS|compute|output) buffer size =\s*([\d.]+) MiB")
BUILD_RE = re.compile(r"build (\d+) \(([0-9a-f]+)\)")
FILE_RE = re.compile(r"file size\s*=\s*([\d.]+) GiB \(([\d.]+) BPW\)")


class ServerError(RuntimeError):
    pass


def port_in_use(host: str, port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def parse_log(text: str) -> dict:
    """Pull build number, bits per weight and buffer sizes (MiB per device) from the log."""
    buffers: dict[str, dict[str, float]] = {}
    for device, kind, mib in BUFFER_RE.findall(text):
        buffers.setdefault(kind.lower(), {})[device] = float(mib)
    info: dict = {"buffers_mib": buffers}
    if m := BUILD_RE.search(text):
        info["build"], info["commit"] = int(m[1]), m[2]
    if m := FILE_RE.search(text):
        info["file_gib"], info["bpw"] = float(m[1]), float(m[2])
    return info


def _same_file(a: str, b: Path) -> bool:
    return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


class LlamaServer:
    """Context manager: start the server, block until /health is OK, stop it on exit."""

    def __init__(self, cmd: list[str], base_url: str, host: str, port: int, model: Path,
                 log_path: Path, health_timeout_s: float):
        self.cmd, self.base_url, self.host, self.port = cmd, base_url, host, port
        self.model, self.log_path, self.health_timeout_s = model, log_path, health_timeout_s
        self.proc: subprocess.Popen | None = None
        self.info: dict = {}

    def __enter__(self) -> "LlamaServer":
        if port_in_use(self.host, self.port):
            raise ServerError(
                f"port {self.port} is already in use. Stop the old llama-server first: "
                "otherwise the harness would measure that server instead of this config."
            )
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._log = open(self.log_path, "w", encoding="utf-8")
        t0 = time.perf_counter()
        self.proc = subprocess.Popen(self.cmd, stdout=self._log, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL)
        try:
            self._wait_healthy()
            self._check_model()
        except BaseException:
            self.stop()
            raise
        self.info = parse_log(self.log_path.read_text(encoding="utf-8", errors="replace"))
        self.info["load_s"] = round(time.perf_counter() - t0, 2)
        return self

    def __exit__(self, *exc) -> None:
        self.stop()

    def _wait_healthy(self) -> None:
        assert self.proc is not None
        deadline = time.perf_counter() + self.health_timeout_s
        while time.perf_counter() < deadline:
            if self.proc.poll() is not None:
                raise ServerError(f"llama-server exited with code {self.proc.returncode} "
                                  f"while loading; last log lines:\n{self.log_tail()}")
            try:
                if requests.get(f"{self.base_url}/health", timeout=2).status_code == 200:
                    return
            except requests.RequestException:
                pass
            time.sleep(0.25)
        raise ServerError(f"llama-server not healthy after {self.health_timeout_s}s")

    def _check_model(self) -> None:
        props = requests.get(f"{self.base_url}/props", timeout=10).json()
        if not _same_file(props.get("model_path", ""), self.model):
            raise ServerError(f"server reports model {props.get('model_path')!r}, expected {self.model}")

    def log_tail(self, n: int = 15) -> str:
        lines = self.log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-n:])

    def alive(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
        if getattr(self, "_log", None) and not self._log.closed:
            self._log.close()
