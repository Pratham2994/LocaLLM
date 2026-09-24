"""Run tasks against configs: start server -> run each task N times -> stop server.

Resumable: a run is skipped when results/runs.jsonl already holds the same
(machine, config, config_hash, task, prompt_hash, repeat). Results are only ever appended.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from . import checks, client
from .config import ROOT, Machine, RunConfig
from .server import LlamaServer, ServerError
from .tasks import Task, TaskSet

RESULTS_DIR = ROOT / "results"
RUNS_FILE = RESULTS_DIR / "runs.jsonl"
LOG_DIR = RESULTS_DIR / "logs"


def run_key(row: dict) -> tuple:
    return (row["machine"], row["config"], row["config_hash"], row["task"], row["prompt_hash"], row["repeat"])


def load_done(path: Path = RUNS_FILE) -> set[tuple]:
    done: set[tuple] = set()
    if not path.exists():
        return done
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                done.add(run_key(json.loads(line)))
            except (json.JSONDecodeError, KeyError):
                print(f"warning: {path.name} line {n} is damaged; ignoring it")
    return done


def append_row(row: dict, path: Path = RUNS_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def plan(cfg: RunConfig, tasks: list[Task], machine: Machine, repeats: int, done: set[tuple]) -> list[tuple[Task, int]]:
    """Repeat-major order (every task once, then every task again), so laptop heat
    drift spreads evenly over tasks instead of hitting the last ones hardest."""
    todo = []
    for r in range(repeats):
        for t in tasks:
            key = (machine.name, cfg.name, cfg.config_hash, t.id, t.prompt_hash, r)
            if t.runs_with(cfg.thinking) and key not in done:
                todo.append((t, r))
    return todo


def _fmt(v: float | None, spec: str) -> str:
    return "-" if v is None else format(v, spec)


def run_config(cfg: RunConfig, taskset: TaskSet, tasks: list[Task], machine: Machine,
               repeats: int, dry_run: bool = False) -> None:
    todo = plan(cfg, tasks, machine, repeats, load_done())
    applicable = sum(t.runs_with(cfg.thinking) for t in tasks) * repeats
    print(f"\n== {cfg.name}  (hash {cfg.config_hash}, machine {machine.name})")
    print(f"   model {cfg.model}  [{cfg.model_bytes / 1e9:.2f} GB]")
    print(f"   {len(todo)} runs to do, {applicable - len(todo)} of {applicable} already in {RUNS_FILE.name}",
          flush=True)
    cmd = cfg.server_command(machine)
    if dry_run:
        print("   server:", " ".join(cmd))
        for t, r in todo:
            print(f"   would run {t.id} r{r}")
        return
    if not todo:
        return

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = LOG_DIR / f"{cfg.name}__{stamp}.log"
    passed = graded = 0
    with LlamaServer(cmd, machine.base_url, machine.host, machine.port, cfg.model,
                     log_path, machine.health_timeout_s) as srv:
        info = srv.info
        print(f"   server up in {info['load_s']}s, build {info.get('build')}, "
              f"buffers {json.dumps(info['buffers_mib'])}", flush=True)
        for i, (task, r) in enumerate(todo, 1):
            started = datetime.now().astimezone().isoformat(timespec="seconds")
            res = client.chat(machine.base_url, task.prompt, thinking=cfg.thinking,
                              sampling=cfg.sampling, max_tokens=cfg.max_tokens,
                              timeout_s=cfg.request_timeout_s)
            if res.error:
                chk = checks.CheckResult(False, f"request failed: {res.error}")
            else:
                chk = checks.run_check(task, res.answer, machine.tools, taskset.fixtures)
            row = {
                "ts": started, "machine": machine.name,
                "config": cfg.name, "config_hash": cfg.config_hash,
                "task": task.id, "prompt_hash": task.prompt_hash, "repeat": r,
                "category": task.category, "lang": task.lang, "check": task.check,
                "passed": chk.passed, "check_detail": chk.detail,
                "model_file": cfg.model.name, "model_bytes": cfg.model_bytes,
                "backend": cfg.backend.name, "threads": cfg.backend.threads,
                "ctx": cfg.ctx, "kv_cache": cfg.kv_cache, "thinking": cfg.thinking,
                "sampling_preset": cfg.sampling_preset, "sampling": cfg.sampling,
                "max_tokens": cfg.max_tokens,
                **res.to_dict(),
                "server": {**info, "cmd": cmd},
            }
            append_row(row)
            if chk.passed is not None:
                graded += 1
                passed += chk.passed
            verdict = {True: "PASS", False: "FAIL", None: "MANUAL"}[chk.passed]
            print(f"   [{i:>3}/{len(todo)}] {task.id:<28} r{r} {verdict:<6} "
                  f"{res.wall_s:6.1f}s  ttfa {_fmt(res.ttfa_s, '.1f')}s  "
                  f"think {res.thinking_tokens:>5}  ans {_fmt(res.answer_tokens, '>4')}  "
                  f"{_fmt(res.decode_tok_s, '.1f')} tok/s  {res.finish_reason or ''}", flush=True)
            if res.error and not srv.alive():
                raise ServerError(f"llama-server died during {task.id}; log tail:\n{srv.log_tail()}")
    print(f"   done: {passed}/{graded} auto-graded runs passed this session")
