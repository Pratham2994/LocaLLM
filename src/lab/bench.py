"""Wrap llama-bench (milestone 5): same model/backend/threads as a config, results in one table.

Appends one line per llama-bench test to results/bench.jsonl; `lab report` shows them.
"""

import json
import subprocess
from datetime import datetime

from .config import ConfigError, Machine, RunConfig
from .runner import RESULTS_DIR, append_row
from .server import port_in_use

BENCH_FILE = RESULTS_DIR / "bench.jsonl"


def run_bench(cfg: RunConfig, machine: Machine, pp: str, tg: str, depth: str, reps: int) -> None:
    exe = next((cfg.backend.dir / n for n in ("llama-bench.exe", "llama-bench")
                if (cfg.backend.dir / n).exists()), None)
    if exe is None:
        raise ConfigError(f"no llama-bench in {cfg.backend.dir}")
    if port_in_use(machine.host, machine.port):
        print("   warning: a llama-server is running; it will slow the benchmark")
    cmd = [str(exe), "-m", str(cfg.model), "-t", str(cfg.backend.threads), *cfg.backend.args,
           "-p", pp, "-n", tg, "-d", depth, "-r", str(reps), "-o", "jsonl"]
    if cfg.kv_cache != "f16":
        cmd += ["-ctk", cfg.kv_cache, "-ctv", cfg.kv_cache]
    # A MoE config keeps some experts in system RAM; without the same split llama-bench
    # over-fills the GPU and measures the spill into shared memory, not the model.
    args = list(cfg.server_args)
    for flag in ("--n-cpu-moe", "-ncmoe"):
        if flag in args[:-1]:
            cmd += ["-ncmoe", args[args.index(flag) + 1]]
            break
    print(f"\n== bench: {cfg.name}\n   {' '.join(cmd)}", flush=True)
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise ConfigError(f"llama-bench failed ({proc.returncode}):\n{proc.stderr[-1500:]}")
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    for line in proc.stdout.splitlines():
        if not line.startswith("{"):
            continue
        test = json.loads(line)
        append_row({"ts": stamp, "machine": machine.name, "config": cfg.name,
                     "backend": cfg.backend.name, **test}, BENCH_FILE)
        print(f"   {bench_test_name(test):<18} {test.get('avg_ts', 0):8.2f} +/- {test.get('stddev_ts', 0):.2f} t/s",
              flush=True)


def bench_test_name(t: dict) -> str:
    name = f"pp{t.get('n_prompt')}" if t.get("n_prompt") else f"tg{t.get('n_gen')}"
    name += f" @ d{t['n_depth']}" if t.get("n_depth") else ""
    return name + (f" ncmoe{t['n_cpu_moe']}" if t.get("n_cpu_moe") else "")
