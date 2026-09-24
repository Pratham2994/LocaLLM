"""Command line: `uv run lab <command>`. See `uv run lab --help`."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import requests

from .checks import run_check
from .client import request_body
from .config import CONFIG_DIR, ConfigError, load_machine, load_run_config
from .runner import LOG_DIR, run_config
from .server import LlamaServer, ServerError
from .tasks import load_tasks


def _config_paths(given: list[str]) -> list[Path]:
    paths = [Path(p) for p in given] if given else sorted(CONFIG_DIR.glob("*.yaml"))
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        raise ConfigError(f"config file(s) not found: {missing}")
    return paths


def cmd_run(args: argparse.Namespace) -> int:
    machine = load_machine(args.machine)
    taskset = load_tasks()
    tasks = taskset.select(args.tasks)
    configs = [load_run_config(p, machine) for p in _config_paths(args.configs)]  # validate all first
    dupes = sorted(n for n, c in Counter(c.name for c in configs).items() if c > 1)
    if dupes:
        raise ConfigError(f"config names must be unique (they key the results): {dupes}")
    for cfg in configs:
        run_config(cfg, taskset, tasks, machine, args.repeats or cfg.repeats, dry_run=args.dry_run)
    return 0


def cmd_selftest(args: argparse.Namespace) -> int:
    """Every auto-checked task must PASS its `reference` answer and FAIL its `wrong` one.
    This proves the checks before any model is blamed for failing them."""
    machine = load_machine(args.machine)
    taskset = load_tasks()
    problems = warnings = 0
    for t in taskset.select(args.tasks):
        if t.check == "manual":
            print(f"  skip  {t.id:<28} manual")
            continue
        results = [("reference", run_check(t, t.reference or "", machine.tools, taskset.fixtures), True)]
        if t.wrong is not None:
            results.append(("wrong answer", run_check(t, t.wrong, machine.tools, taskset.fixtures), False))
        notes, status = [], "ok"
        for label, res, should_pass in results:
            if res.passed is None:  # the OS refused to run it: environment, not the task
                notes.append(f"{label} NOT GRADED ({res.detail})")
                status = "warn" if status == "ok" else status
            elif res.passed != should_pass:
                notes.append(f"{label} {'FAILS' if should_pass else 'PASSES (tests too weak)'}:\n"
                             + "        " + res.detail.replace("\n", "\n        "))
                status = "BAD"
            else:
                notes.append(f"{label} {'passes' if should_pass else 'is caught'}")
        print(f"{status:>6}  {t.id:<28} " + ", ".join(notes))
        problems += status == "BAD"
        warnings += status == "warn"
    print(f"\n{problems} problem(s), {warnings} warning(s)")
    return 1 if problems else 0


def cmd_tasks(args: argparse.Namespace) -> int:
    taskset = load_tasks()
    tasks = taskset.select(args.tasks)
    for t in tasks:
        print(f"{t.id:<28} {t.category:<22} {t.lang:<7} {t.check:<13} thinking={t.thinking}")
    print(f"\n{len(tasks)} tasks; by category: {dict(Counter(t.category for t in tasks))}")
    return 0


def cmd_probe(args: argparse.Namespace) -> int:
    """Start the server for one config, send one non-streamed request, print the raw JSON.
    Use it after any llama.cpp update, before trusting response fields."""
    machine = load_machine(args.machine)
    cfg = load_run_config(Path(args.config), machine)
    cmd = cfg.server_command(machine)
    with LlamaServer(cmd, machine.base_url, machine.host, machine.port, cfg.model,
                     LOG_DIR / f"probe__{cfg.name}.log", machine.health_timeout_s) as srv:
        print("server info:", json.dumps(srv.info, indent=2))
        body = request_body(args.prompt, thinking=cfg.thinking, sampling=cfg.sampling,
                            max_tokens=cfg.max_tokens, stream=False)
        r = requests.post(f"{machine.base_url}/v1/chat/completions", json=body, timeout=cfg.request_timeout_s)
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="lab", description="Local LLM test harness (LOCAL_LLM_LAB.md section 7).")
    p.add_argument("--machine", help="machine file stem in configs/machines (default: match hostname)")
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("run", help="run tasks for configs (default: all configs/*.yaml); resumable")
    r.add_argument("configs", nargs="*", help="config YAML files")
    r.add_argument("--tasks", nargs="+", help="task ids or glob patterns, e.g. sql-* py-parse-date")
    r.add_argument("--repeats", type=int, help="override the config's repeats")
    r.add_argument("--dry-run", action="store_true", help="show the plan and server command only")
    r.set_defaults(func=cmd_run)

    s = sub.add_parser("selftest", help="check every task's reference passes and wrong answer fails")
    s.add_argument("--tasks", nargs="+")
    s.set_defaults(func=cmd_selftest)

    t = sub.add_parser("tasks", help="list tasks")
    t.add_argument("--tasks", nargs="+")
    t.set_defaults(func=cmd_tasks)

    pr = sub.add_parser("probe", help="start one config's server and print one raw JSON response")
    pr.add_argument("config")
    pr.add_argument("--prompt", default="What is 17 × 23? Answer with just the number.")
    pr.set_defaults(func=cmd_probe)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except (ConfigError, ServerError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nstopped by user; finished runs are saved and will be skipped next time", file=sys.stderr)
        return 130
