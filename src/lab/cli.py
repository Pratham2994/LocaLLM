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


def cmd_needle(args: argparse.Namespace) -> int:
    from .needle import run_needle
    machine = load_machine(args.machine)
    run_needle(load_run_config(Path(args.config), machine), machine, args.sizes, args.depths)
    return 0


def cmd_bench(args: argparse.Namespace) -> int:
    from .bench import run_bench
    machine = load_machine(args.machine)
    for p in _config_paths(args.configs):
        run_bench(load_run_config(p, machine), machine, args.pp, args.tg, args.depth, args.reps)
    return 0


def cmd_agent(args: argparse.Namespace) -> int:
    """Agent tier (tasks/agent.yaml): tool-call tasks and mini repo tasks, results in results/agent.jsonl."""
    from . import agent
    machine = load_machine(args.machine)
    tasks = agent.select(agent.load_agent_tasks(), args.tasks)
    if args.selftest:
        return agent.selftest(tasks, machine)
    if args.list:
        for t in tasks:
            print(f"{t.id:<26} {t.kind:<5} {t.category:<16} max_steps={t.max_steps}")
        print(f"\n{len(tasks)} agent tasks")
        return 0
    if not args.configs:
        raise ConfigError("name the config file(s), e.g. configs\\agent\\<name>.yaml")
    configs = [load_run_config(p, machine) for p in _config_paths(args.configs)]
    for cfg in configs:
        agent.run_agent_config(cfg, tasks, machine, args.repeats or cfg.repeats, dry_run=args.dry_run)
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    from .report import build_report
    path = build_report()
    text = path.read_text(encoding="utf-8")
    overview = text.split("## Overview", 1)[1].split("##", 1)[0].strip()
    print(overview)
    print(f"\nwrote {path} and charts in {path.parent / 'charts'}")
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

    ag = sub.add_parser("agent", help="agent tier: tool-call and mini repo tasks (tasks/agent.yaml); resumable")
    ag.add_argument("configs", nargs="*", help="config YAML files (configs/agent/*.yaml)")
    ag.add_argument("--tasks", nargs="+", help="agent task ids or glob patterns, e.g. tc-* ag-py-*")
    ag.add_argument("--repeats", type=int, help="override the config's repeats")
    ag.add_argument("--dry-run", action="store_true", help="show the plan and server command only")
    ag.add_argument("--selftest", action="store_true", help="prove the graders: references pass, wrong answers fail")
    ag.add_argument("--list", action="store_true", help="list the agent tasks")
    ag.set_defaults(func=cmd_agent)

    rp = sub.add_parser("report", help="write results/report.md and charts from runs.jsonl")
    rp.set_defaults(func=cmd_report)

    nd = sub.add_parser("needle", help="needle-in-a-haystack test at several context sizes")
    nd.add_argument("config")
    nd.add_argument("--sizes", nargs="+", type=int, default=[4096, 16384, 32768], help="prompt tokens")
    nd.add_argument("--depths", nargs="+", type=float, default=[0.5], help="needle position, 0 = start, 1 = end")
    nd.set_defaults(func=cmd_needle)

    bn = sub.add_parser("bench", help="llama-bench with each config's model/backend/threads")
    bn.add_argument("configs", nargs="*", help="config YAML files (default: all)")
    bn.add_argument("--pp", default="512", help="prompt sizes, comma-separated (llama-bench -p)")
    bn.add_argument("--tg", default="128", help="generation sizes (llama-bench -n)")
    bn.add_argument("--depth", default="0", help="context depths (llama-bench -d)")
    bn.add_argument("--reps", type=int, default=3)
    bn.set_defaults(func=cmd_bench)

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
