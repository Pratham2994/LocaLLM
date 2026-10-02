"""Aggregate results/runs.jsonl into results/report.md and PNG charts (milestone 3).

Only current results count: rows whose prompt still matches tasks.yaml, and for each
(machine, config) only the newest config_hash. Older rows stay in runs.jsonl untouched.
"""

import json
import re
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .runner import RESULTS_DIR, RUNS_FILE  # noqa: E402
from .tasks import load_tasks  # noqa: E402

REPORT_FILE = RESULTS_DIR / "report.md"
CHART_DIR = RESULTS_DIR / "charts"
QUANT_RE = re.compile(r"(UD-IQ\d_\w+|IQ\d_\w+|(?:UD-)?Q\d_K_XL|Q\d_K_[SML]|Q\d_K|Q\d_\d|BF16|F16|F32)", re.I)
QUANT_ORDER = ["UD-IQ2_XXS", "IQ2_XXS", "IQ2_XS", "Q2_K", "Q3_K_M", "Q4_K_M", "Q5_K_M", "Q6_K", "Q8_0", "BF16", "F16"]

# Chart tokens (dataviz reference palette, light surface).
SURFACE, INK, INK2, MUTED, GRID, BASELINE, SERIES = (
    "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#2a78d6")


@dataclass
class Summary:
    machine: str
    config: str
    model_file: str
    model_bytes: int
    backend: str
    thinking: bool
    rows: list = field(default_factory=list)

    @property
    def graded(self) -> list:
        return [r for r in self.rows if r["passed"] is not None]

    @property
    def passed(self) -> int:
        return sum(r["passed"] for r in self.graded)

    @property
    def pass_rate(self) -> float:
        return self.passed / len(self.graded) if self.graded else 0.0

    @property
    def correct_per_hour(self) -> float:
        hours = sum(r["wall_s"] for r in self.graded) / 3600
        return self.passed / hours if hours else 0.0

    @property
    def quant(self) -> str:
        m = QUANT_RE.search(Path(self.model_file).stem)
        return m.group(1).upper() if m else "?"

    @property
    def label(self) -> str:
        return self.config.replace("-vulkan", "").replace("-nothink", "")

    def median(self, key: str) -> float | None:
        vals = [r[key] for r in self.rows if r.get(key) is not None]
        return statistics.median(vals) if vals else None

    def mean(self, key: str) -> float | None:
        vals = [r[key] for r in self.rows if r.get(key) is not None]
        return statistics.mean(vals) if vals else None

    @property
    def memory_gib(self) -> float:
        """Sum of all llama-server buffers (weights, KV, recurrent state, compute), in GiB."""
        buffers = self.rows[-1]["server"].get("buffers_mib", {})
        return sum(sum(dev.values()) for dev in buffers.values()) / 1024

    def by(self, key: str) -> dict[str, tuple[int, int, int]]:
        """key value -> (passed, graded, manual)."""
        out: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
        for r in self.rows:
            cell = out[r[key]]
            if r["passed"] is None:
                cell[2] += 1
            else:
                cell[0] += r["passed"]
                cell[1] += 1
        return {k: (v[0], v[1], v[2]) for k, v in out.items()}


def load_summaries(path: Path = RUNS_FILE) -> tuple[list[Summary], int]:
    current = {t.id: t.prompt_hash for t in load_tasks().tasks}
    rows = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
    rows = [r for r in rows if current.get(r["task"]) == r["prompt_hash"]]
    newest: dict[tuple, dict] = {}
    for r in rows:
        k = (r["machine"], r["config"])
        if k not in newest or r["ts"] > newest[k]["ts"]:
            newest[k] = r
    groups: dict[tuple, Summary] = {}
    for r in rows:
        k = (r["machine"], r["config"])
        if r["config_hash"] != newest[k]["config_hash"]:
            continue
        if k not in groups:
            groups[k] = Summary(r["machine"], r["config"], r["model_file"], r["model_bytes"],
                                r["backend"], r["thinking"])
        groups[k].rows.append(r)
    return sorted(groups.values(), key=lambda s: -s.correct_per_hour), len(rows)


# ---------------------------------------------------------------- charts

def _style(fig, ax, grid_axis: str) -> None:
    fig.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelcolor=INK2, labelsize=9)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _title(ax, title: str, subtitle: str) -> None:
    ax.set_title(f"{title}\n", loc="left", color=INK, fontsize=11, fontweight="bold")
    ax.text(0, 1.02, subtitle, transform=ax.transAxes, color=INK2, fontsize=8.5)


def _hbar(path: Path, labels: list[str], values: list[float], title: str, subtitle: str,
          xlabel: str, fmt) -> None:
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(labels) + 1.5), dpi=150)
    y = list(range(len(labels)))
    ax.barh(y, values, height=0.62, color=SERIES)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    for yi, v in zip(y, values):
        ax.text(v, yi, f"  {fmt(v)}", va="center", color=INK, fontsize=9)
    ax.set_xlim(0, max(values) * 1.18 if values and max(values) > 0 else 1)
    ax.set_xlabel(xlabel, color=INK2, fontsize=9)
    _title(ax, title, subtitle)
    _style(fig, ax, "x")
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def _scatter_size(path: Path, sums: list[Summary]) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.6), dpi=150)
    xs = [s.model_bytes / 1e9 for s in sums]
    ys = [s.pass_rate * 100 for s in sums]
    ax.scatter(xs, ys, s=70, color=SERIES, edgecolors=SURFACE, linewidths=2, zorder=3)
    for s, x, y in zip(sums, xs, ys):
        ax.annotate(s.label, (x, y), xytext=(6, 5), textcoords="offset points", color=INK2, fontsize=8)
    ax.set_xlabel("Model file size (GB)", color=INK2, fontsize=9)
    ax.set_ylabel("Pass rate (%)", color=INK2, fontsize=9)
    ax.set_ylim(0, 105)
    ax.set_xlim(0, max(xs) * 1.25)
    _title(ax, "Pass rate vs model file size", "Thinking off, auto-graded tasks only")
    _style(fig, ax, "y")
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def _quant_ladder(path: Path, sums: list[Summary]) -> bool:
    ladder = [s for s in sums if s.model_file.startswith("Qwen3.5-4B-") and s.quant in QUANT_ORDER]
    if len(ladder) < 2:
        return False
    ladder.sort(key=lambda s: QUANT_ORDER.index(s.quant))
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
    x = list(range(len(ladder)))
    ys = [s.pass_rate * 100 for s in ladder]
    ax.plot(x, ys, color=SERIES, linewidth=2, marker="o", markersize=8,
            markeredgecolor=SURFACE, markeredgewidth=2, zorder=3)
    for xi, y in zip(x, ys):
        ax.annotate(f"{y:.0f}%", (xi, y), xytext=(0, 9), textcoords="offset points",
                    ha="center", color=INK, fontsize=9)
    ax.set_xticks(x, [f"{s.quant}\n{s.model_bytes / 1e9:.2f} GB" for s in ladder])
    ax.set_ylim(0, 110)
    ax.set_ylabel("Pass rate (%)", color=INK2, fontsize=9)
    _title(ax, "Qwen3.5-4B: pass rate vs quantisation", "Thinking off; fewer bits to the left")
    _style(fig, ax, "y")
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    return True


# ---------------------------------------------------------------- report

def _f(v: float | None, spec: str, suffix: str = "") -> str:
    return "–" if v is None else f"{format(v, spec)}{suffix}"


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def _needle_section() -> list[str]:
    rows = _jsonl(RESULTS_DIR / "needle.jsonl")
    if not rows:
        return []
    out = ["", "## Needle in a haystack (`lab needle`)", "",
           "| Machine | Config | Prompt tokens | Depth | Found | Prefill s | Prefill tok/s | Answer |",
           "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        found = f"**error**: {r['error'][:60]}" if r.get("error") else "yes" if r["found"] else "**no**"
        out.append(f"| {r['machine']} | `{r['config']}` | {r['prompt_tokens'] or '~' + str(r['target_tokens'])} "
                   f"| {r['depth']:.2f} | {found} | {_f(r['prefill_ms'] and r['prefill_ms'] / 1000, '.1f')} "
                   f"| {_f(r['prefill_tok_s'], '.0f')} | `{r['answer'].strip()[:30]}` |")
    return out


def _bench_section() -> list[str]:
    from .bench import bench_test_name
    rows = _jsonl(RESULTS_DIR / "bench.jsonl")
    if not rows:
        return []
    out = ["", "## llama-bench (`lab bench`)", "",
           "| Date | Machine | Config | Build | Test | t/s | ± |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['ts'][:16]} | {r['machine']} | `{r['config']}` | {r.get('build_number', '?')} "
                   f"| {bench_test_name(r)} | {r.get('avg_ts', 0):.2f} | {r.get('stddev_ts', 0):.2f} |")
    return out


AGENT_TIERS = (("Tool calls", "tc-"), ("Small repo tasks", "ag-"), ("Project tasks", "ag-depot-"))


def _agent_tier(task_id: str) -> str:
    return next(name for name, prefix in reversed(AGENT_TIERS) if task_id.startswith(prefix))


def _agent_section() -> list[str]:
    """Agent tier (`lab agent`): current rows only (task text, loop version and config unchanged)."""
    from . import agent
    rows = agent.load_rows()
    if not rows:
        return []
    tasks = agent.load_agent_tasks()
    current = {t.id: t.task_hash for t in tasks}
    newest = {}
    for r in rows:  # the last config_hash seen per config is the current one
        newest[(r["machine"], r["config"])] = r["config_hash"]
    rows = [r for r in rows if current.get(r["task"]) == r["task_hash"] and r.get("agent_version") == agent.AGENT_VERSION
            and newest[(r["machine"], r["config"])] == r["config_hash"]]
    configs = list(dict.fromkeys((r["machine"], r["config"]) for r in rows))

    def cell(sel: list[dict]) -> str:
        graded = [r for r in sel if r["passed"] is not None]
        return f"{sum(r['passed'] for r in graded)}/{len(graded)}" if graded else "–"

    def score(key: tuple) -> float:
        graded = [r for r in rows if (r["machine"], r["config"]) == key and r["passed"] is not None]
        return sum(r["passed"] for r in graded) / len(graded) if graded else 0.0

    configs.sort(key=score, reverse=True)
    out = ["", "## Agent tier (`lab agent`)", "",
           "The model works through tools over several turns (`tasks/agent.yaml`). Tool calls: scripted tools, graded on "
           "the calls and the final answer. Repo and project tasks: the model edits a made-up project with six file "
           "tools; hidden tests decide. Bad calls = unknown tool, invalid arguments or a missing required argument.", "",
           "| Config | Thinking | " + " | ".join(name for name, _ in AGENT_TIERS) + " | All | Median steps (repo) "
           "| Median s per repo task | Largest prompt (tokens) | Bad calls | Not finished |",
           "|---|---|" + "---|" * (len(AGENT_TIERS) + 6)]
    for key in configs:
        mine = [r for r in rows if (r["machine"], r["config"]) == key]
        repo = [r for r in mine if r["kind"] == "repo"]
        tiers = [cell([r for r in mine if _agent_tier(r["task"]) == name]) for name, _ in AGENT_TIERS]
        unfinished = sum(r["finish"] != "final" for r in mine)
        out.append(
            f"| `{key[1]}` | {'on' if mine[0]['thinking'] else 'off'} | " + " | ".join(tiers) + f" | **{cell(mine)}** "
            f"| {_f(statistics.median(r['steps'] for r in repo) if repo else None, '.0f')} "
            f"| {_f(statistics.median(r['wall_s'] for r in repo) if repo else None, '.0f')} "
            f"| {max((r['prompt_tokens_max'] for r in mine), default=0)} | {sum(len(r['bad_calls']) for r in mine)} | {unfinished} |")
    out += ["", "Per agent task (passed / runs):", "",
            "| Task | Tier | " + " | ".join(f"`{c[1].removeprefix('agent-')}`" for c in configs) + " |",
            "|---|---|" + "---|" * len(configs)]
    for t in tasks:
        cells = [cell([r for r in rows if (r["machine"], r["config"]) == key and r["task"] == t.id]) for key in configs]
        out.append(f"| `{t.id}` | {_agent_tier(t.id)} | " + " | ".join(cells) + " |")
    return out


def build_report() -> Path:
    sums, n_rows = load_summaries()
    if not sums:
        raise SystemExit("no current results in runs.jsonl")
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    tasks = load_tasks().tasks
    multi_machine = len({s.machine for s in sums}) > 1
    if multi_machine:
        for s in sums:
            s.config = f"{s.machine}:{s.config}"

    off = [s for s in sums if not s.thinking]
    charts = []
    if off:
        _hbar(CHART_DIR / "correct_per_hour.png", [f"{s.label} ({s.pass_rate:.0%} pass)" for s in off],
              [s.correct_per_hour for s in off], "Correct answers per hour",
              "Thinking off. Read with the pass rate: fast but wrong is no use",
              "Correct answers per hour", lambda v: f"{v:.0f}")
        charts.append(("Correct answers per hour", "correct_per_hour.png"))
        by_time = sorted(off, key=lambda s: s.median("wall_s") or 0)
        _hbar(CHART_DIR / "time_per_task.png", [s.label for s in by_time], [s.median("wall_s") or 0 for s in by_time],
              "Median time per task", "Thinking off; wall time from request to last token",
              "Seconds", lambda v: f"{v:.1f} s")
        charts.append(("Median time per task", "time_per_task.png"))
        _scatter_size(CHART_DIR / "pass_rate_vs_size.png", off)
        charts.append(("Pass rate vs file size", "pass_rate_vs_size.png"))
        if _quant_ladder(CHART_DIR / "quant_ladder_4b.png", off):
            charts.append(("Qwen3.5-4B quant ladder", "quant_ladder_4b.png"))

    lines = [
        "# Harness report",
        "",
        f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} from `{RUNS_FILE.name}` "
        f"({n_rows} current runs; {len(tasks)} tasks in `tasks.yaml`). Sorted by correct answers per hour.",
        "",
        "- **Correct answers per hour** = passed auto-graded runs ÷ hours of wall time spent on them.",
        "- Thinking-on configs run only the tasks marked `thinking: on/both`, so compare them with care.",
        "- Memory = sum of llama-server buffers (weights + KV cache + recurrent state + compute).",
        "",
        "## Overview",
        "",
        "| Config | Quant | File GB | Thinking | Runs | Passed | Pass rate | Correct/hour | Median s/task "
        "| Median first answer s | Decode tok/s | Mean tokens/run | Memory GiB | Manual | Cut off |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in sums:
        cut = sum(r["finish_reason"] == "length" for r in s.rows)
        manual = len(s.rows) - len(s.graded)
        lines.append(
            f"| `{s.config}` | {s.quant} | {s.model_bytes / 1e9:.2f} | {'on' if s.thinking else 'off'} "
            f"| {len(s.rows)} | {s.passed}/{len(s.graded)} | **{s.pass_rate:.0%}** | **{s.correct_per_hour:.0f}** "
            f"| {_f(s.median('wall_s'), '.1f')} | {_f(s.median('ttfa_s'), '.1f')} | {_f(s.median('decode_tok_s'), '.1f')} "
            f"| {_f(s.mean('completion_tokens'), '.0f')} | {s.memory_gib:.2f} | {manual} | {cut} |")

    cats = sorted({t.category for t in tasks}, key=[t.category for t in tasks].index)
    lines += ["", "## Pass rate by category", "",
              "| Config | " + " | ".join(c.replace("_", " ") for c in cats) + " |",
              "|---|" + "---|" * len(cats)]
    for s in sums:
        by_cat = s.by("category")
        cells = []
        for c in cats:
            p, g, _m = by_cat.get(c, (0, 0, 0))
            cells.append(f"{p}/{g}" if g else "–")
        lines.append(f"| `{s.label}` | " + " | ".join(cells) + " |")

    lines += ["", "## Per task", "",
              "✓ = passed every repeat, ✗ = failed every repeat, `p/n` = mixed, M = needs manual grading, "
              "blank = not run.", "",
              "| Task | Category | " + " | ".join(f"`{s.label}`" for s in sums) + " |",
              "|---|---|" + "---|" * len(sums)]
    per_task = [s.by("task") for s in sums]
    for t in tasks:
        cells = []
        for bt in per_task:
            p, g, m = bt.get(t.id, (0, 0, 0))
            cells.append("" if not (g or m) else "M" if m and not g else
                         "✓" if p == g else "✗" if p == 0 else f"{p}/{g}")
        lines.append(f"| `{t.id}` | {t.category.replace('_', ' ')} | " + " | ".join(cells) + " |")

    if charts:
        lines += ["", "## Charts", ""]
        for title, file in charts:
            lines += [f"![{title}](charts/{file})", ""]
    lines += _agent_section() + _needle_section() + _bench_section()
    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return REPORT_FILE
