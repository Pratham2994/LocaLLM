"""Agent tier: can a model work through tools, over several turns?

Two kinds of task in tasks/agent.yaml (LOCAL_LLM_LAB.md 9.11):
- `tool`: the task brings its own scripted tools with canned results. Graded on the calls the
  model makes (right tool, right arguments, none it was not offered) and on its final answer.
- `repo`: a small made-up project is written into a fresh temp folder. The model gets six file
  tools and must change the code. Graded by hidden tests run on a copy of the folder, so only
  the result counts, not the route.

Safety: the model never gets a shell. File tools cannot leave the temp folder, and tests run
through the same sandbox as `checks.py` (minimal environment, timeout, Python audit hook,
Node permission model).
"""

import hashlib
import json
import posixpath
import re
import shutil
import statistics
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from . import client
from .checks import DEFAULT_TIMEOUT_S, PY_GUARD, Blocked, CheckResult, _run
from .config import ROOT, ConfigError, Machine, RunConfig, check_keys, read_yaml
from .runner import LOG_DIR, RESULTS_DIR, append_row
from .server import LlamaServer, ServerError

AGENT_FILE = ROOT / "tasks" / "agent.yaml"
PROJECT_DIR = ROOT / "tasks" / "projects"     # shared base projects for `repo` tasks (`base: <name>`)
AGENT_RUNS = RESULTS_DIR / "agent.jsonl"
TRANSCRIPT_DIR = RESULTS_DIR / "agent_logs"   # full conversations, for reading failures; not committed
MEMORY_FILE = RESULTS_DIR / "memory.jsonl"     # one line per config run: RAM and GPU memory with the model loaded
AGENT_VERSION = 2          # part of the resume key: raise it when the loop or the repo tools change
#                            (2: `run_file` tool, hidden checks give a score, new repo system prompt)
RESULT_CHARS = 12_000      # a longer tool result is cut, with a note, like real agent tools do
DEFAULT_STEPS = {"tool": 6, "repo": 25}
TASK_WALL_S = 900
TEST_FILE = {"python": "run_tests.py", "js": "run_tests.cjs"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

REPO_SYSTEM = (
    "You are a coding agent working in a small software project. Use the tools to look at the files, "
    "change the code, run the tests and run small scripts of your own. Do not ask the user questions. "
    "The tests in the project cover only a part of the expected behaviour: the written rules of the "
    "project (README, docstrings, the task) all count. When the work is complete, reply with a short "
    "summary and no tool call."
)
RESULT_RE = re.compile(r"^RESULT (\d+)/(\d+)\s*$", re.M)   # printed by test files that count rule groups
TOOL_SYSTEM = "You are a helpful assistant. Use the available tools when they are needed to answer."


def _fn(name: str, description: str, properties: dict, required: list[str]) -> dict:
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": properties, "required": required}}}


_PATH = {"type": "string", "description": "Path relative to the project root, e.g. src/app.py"}
REPO_TOOLS = [
    _fn("list_files", "List all files of the project, one path per line.", {}, []),
    _fn("read_file", "Return the full text of one file.", {"path": _PATH}, ["path"]),
    _fn("search", "Search all project files for a regular expression. Returns matching lines as path:line: text.",
        {"pattern": {"type": "string", "description": "Python regular expression"}}, ["pattern"]),
    _fn("write_file", "Create a file or replace its whole content.",
        {"path": _PATH, "content": {"type": "string", "description": "The complete new file content"}},
        ["path", "content"]),
    _fn("edit_file", "Replace one exact piece of text in a file. old_text must occur exactly once in the file.",
        {"path": _PATH,
         "old_text": {"type": "string", "description": "Exact text to replace, including indentation"},
         "new_text": {"type": "string", "description": "Text to put in its place"}},
        ["path", "old_text", "new_text"]),
    _fn("run_tests", "Run the project's tests and return their output and exit code.", {}, []),
    _fn("run_file", "Run one script of the project (for example a small file you wrote to try something out) "
        "and return its output and exit code. It runs with the project root as the working folder.",
        {"path": _PATH}, ["path"]),
]


# ---------------------------------------------------------------- tasks

@dataclass(frozen=True)
class AgentTask:
    id: str
    kind: str            # "tool" | "repo"
    category: str
    prompt: str
    system: str
    max_steps: int
    spec: dict = field(default_factory=dict)   # tool: tools, expect; repo: lang, files, hidden
    reference: dict | None = None
    wrong: dict | None = None
    notes: str | None = None

    @property
    def task_hash(self) -> str:
        """Hash of everything the model sees and everything that grades it."""
        key = {"system": self.system, "prompt": self.prompt, "max_steps": self.max_steps, "spec": self.spec}
        return hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()[:12]

    @property
    def tools(self) -> list[dict]:
        if self.kind == "repo":
            return REPO_TOOLS
        return [_fn(t["name"], t["description"], (t.get("parameters") or {}).get("properties", {}),
                    (t.get("parameters") or {}).get("required", [])) for t in self.spec["tools"]]


def project_files(name: str, where: str) -> dict[str, str]:
    """All files of a shared base project, tasks/projects/<name>/, as {relative path: text}."""
    root = PROJECT_DIR / name
    if not root.is_dir():
        raise ConfigError(f"{where}: no base project {root}")
    return {p.relative_to(root).as_posix(): p.read_text(encoding="utf-8")
            for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def _reference_file(path: str, value: object, base: dict, files: dict, where: str) -> str:
    """A reference file is the full new text, "@base" (the base project's version), or
    {patch: [{old, new}]}: text changes applied to the file as the task starts with it."""
    if value == "@base":
        return base[path]
    if isinstance(value, dict):
        text = files[path]
        for change in value["patch"]:
            if text.count(change["old"]) != 1:
                raise ConfigError(f"{where}: reference patch: `old` must occur exactly once in {path}: {change['old']!r}")
            text = text.replace(change["old"], change["new"])
        return text
    return str(value)


def load_agent_tasks(path: Path = AGENT_FILE) -> list[AgentTask]:
    data = read_yaml(path)
    check_keys(str(path), data, {"tasks"}, set())
    tasks, seen = [], set()
    common_req = {"id", "kind", "category", "prompt"}
    common_opt = {"system", "max_steps", "notes", "reference", "wrong"}
    for i, raw in enumerate(data["tasks"]):
        where = f"{path}: task #{i + 1} ({raw.get('id', '?')})"
        kind = raw.get("kind")
        if kind == "tool":
            check_keys(where, raw, common_req | {"tools", "expect", "reference"}, common_opt)
            for t in raw["tools"]:
                check_keys(f"{where}: tool {t.get('name', '?')}", t, {"name", "description"},
                           {"parameters", "returns", "results"})
            check_keys(f"{where}: expect", raw["expect"], set(),
                       {"calls", "ordered", "forbid", "max_calls", "min_calls", "final_contains",
                        "final_not_contains", "final_regex"})
            spec = {"tools": raw["tools"], "expect": raw["expect"]}
        elif kind == "repo":
            check_keys(where, raw, common_req | {"lang", "files", "hidden", "reference"},
                       common_opt | {"base", "mutate", "visible_pass"})
            if raw["lang"] not in TEST_FILE:
                raise ConfigError(f"{where}: lang must be one of {sorted(TEST_FILE)}")
            if TEST_FILE[raw["lang"]] not in raw["files"] or TEST_FILE[raw["lang"]] not in raw["hidden"]:
                raise ConfigError(f"{where}: `files` and `hidden` must both hold {TEST_FILE[raw['lang']]}")
            base: dict[str, str] = {}   # one project folder, or several laid over each other in order
            for name in ([raw["base"]] if isinstance(raw.get("base"), str) else raw.get("base") or []):
                base |= project_files(name, where)
            files = base | raw["files"]
            for change in raw.get("mutate") or []:
                check_keys(f"{where}: mutate", change, {"path", "old", "new"}, set())
                if files.get(change["path"], "").count(change["old"]) != 1:
                    raise ConfigError(f"{where}: mutate: `old` must occur exactly once in {change['path']}")
                files[change["path"]] = files[change["path"]].replace(change["old"], change["new"])
            raw = raw | {"reference": {p: _reference_file(p, v, base, files, where) for p, v in raw["reference"].items()}}
            spec = {"lang": raw["lang"], "files": files, "hidden": raw["hidden"]}
            if raw.get("visible_pass"):
                spec["visible_pass"] = True
        else:
            raise ConfigError(f"{where}: kind must be tool or repo")
        if not ID_RE.match(raw["id"]) or raw["id"] in seen:
            raise ConfigError(f"{where}: id must be unique, lowercase letters, digits and hyphens")
        seen.add(raw["id"])
        tasks.append(AgentTask(
            id=raw["id"], kind=kind, category=raw["category"], prompt=raw["prompt"].strip(),
            system=(raw.get("system") or (REPO_SYSTEM if kind == "repo" else TOOL_SYSTEM)).strip(),
            max_steps=int(raw.get("max_steps") or DEFAULT_STEPS[kind]), spec=spec,
            reference=raw.get("reference"), wrong=raw.get("wrong"), notes=raw.get("notes"),
        ))
    return tasks


def select(tasks: list[AgentTask], patterns: list[str] | None) -> list[AgentTask]:
    from fnmatch import fnmatch
    if not patterns:
        return tasks
    chosen = [t for t in tasks if any(fnmatch(t.id, p) for p in patterns)]
    if not chosen:
        raise ConfigError(f"no agent task matches {patterns}")
    return chosen


# ---------------------------------------------------------------- matching arguments

def _norm_str(s: str, key: str | None) -> str:
    s = " ".join(s.split()).casefold()
    if key in ("path", "file", "filename"):
        s = posixpath.normpath(s.replace("\\", "/"))
    return s


def matches(spec: object, got: object, key: str | None = None) -> bool:
    """Does an argument value satisfy the task's expectation?
    Plain values: strings compare without case and extra spaces (paths also without ./), numbers and
    booleans by value and type, lists element by element, mappings as a subset.
    Matchers: {$contains: text}, {$regex: pattern}, {$exact: value}, {$any: [options]}."""
    if isinstance(spec, dict) and len(spec) == 1 and next(iter(spec)).startswith("$"):
        op, arg = next(iter(spec.items()))
        if op == "$contains":
            return isinstance(got, str) and str(arg).casefold() in got.casefold()
        if op == "$regex":
            return isinstance(got, str) and re.search(arg, got, re.S) is not None
        if op == "$exact":
            return got == arg
        if op == "$any":
            return any(matches(a, got, key) for a in arg)
        raise ConfigError(f"unknown matcher {op}")
    if isinstance(spec, dict):
        return isinstance(got, dict) and all(k in got and matches(v, got[k], k) for k, v in spec.items())
    if isinstance(spec, list):
        return isinstance(got, list) and len(got) == len(spec) and all(matches(s, g, key) for s, g in zip(spec, got))
    if isinstance(spec, bool) or isinstance(got, bool):
        return isinstance(spec, bool) and isinstance(got, bool) and spec == got
    if isinstance(spec, (int, float)):
        return isinstance(got, (int, float)) and float(spec) == float(got)
    if isinstance(spec, str):
        return isinstance(got, str) and _norm_str(spec, key) == _norm_str(got, key)
    return spec == got


# ---------------------------------------------------------------- executors

class MockTools:
    """Scripted tools of a `tool` task: canned results chosen by the arguments."""

    def __init__(self, task: AgentTask):
        self.defs = {t["name"]: t for t in task.spec["tools"]}

    def call(self, name: str, args: dict) -> tuple[str, str | None]:
        """Returns (result text for the model, reason if this was a bad call)."""
        tool = self.defs[name]
        missing = [p for p in (tool.get("parameters") or {}).get("required", []) if p not in args]
        if missing:
            return f"ERROR: missing required argument(s): {', '.join(missing)}", f"{name}: missing {missing}"
        for rule in tool.get("results") or []:
            if matches(rule["when"], args):
                return str(rule["returns"]), None
        return str(tool.get("returns", "ok")), None


class Workspace:
    """Real file tools of a `repo` task, limited to one temp folder."""

    def __init__(self, root: Path, lang: str, machine_tools: dict):
        self.root, self.lang, self.machine_tools = root, lang, machine_tools
        self.defs = {t["function"]["name"]: t["function"] for t in REPO_TOOLS}

    def _resolve(self, rel: object) -> Path | None:
        if not isinstance(rel, str) or not rel.strip():
            return None
        p = (self.root / rel.strip().replace("\\", "/")).resolve()
        return p if p == self.root or self.root in p.parents else None

    def _files(self) -> list[Path]:
        return sorted(p for p in self.root.rglob("*") if p.is_file() and "__pycache__" not in p.parts)

    def call(self, name: str, args: dict) -> tuple[str, str | None]:
        missing = [p for p in self.defs[name]["parameters"]["required"] if p not in args]
        if missing:
            return f"ERROR: missing required argument(s): {', '.join(missing)}", f"{name}: missing {missing}"
        if name == "list_files":
            return "\n".join(p.relative_to(self.root).as_posix() for p in self._files()), None
        if name == "run_tests":
            code, out = run_project_tests(self.root, self.lang, self.machine_tools)
            return f"{out.strip()}\n\nexit code: {code}", None
        if name == "search":
            try:
                rx = re.compile(str(args["pattern"]))
            except re.error as e:
                return f"ERROR: invalid regular expression: {e}", None
            hits = []
            for p in self._files():
                for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                    if rx.search(line):
                        hits.append(f"{p.relative_to(self.root).as_posix()}:{n}: {line.strip()}")
            return "\n".join(hits[:60]) or "no matches", None
        path = self._resolve(args["path"])
        if path is None:
            return "ERROR: path must be inside the project (use a relative path such as src/app.py)", None
        if name == "run_file":
            if not path.is_file():
                return f"ERROR: no such file: {args['path']}", None
            code, out = run_project_tests(self.root, self.lang, self.machine_tools, path.relative_to(self.root).as_posix())
            return f"{out.strip()}\n\nexit code: {code}", None
        if name == "read_file":
            if not path.is_file():
                return f"ERROR: no such file: {args['path']}. Use list_files to see the files.", None
            return path.read_text(encoding="utf-8", errors="replace"), None
        if name == "write_file":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(args["content"]), encoding="utf-8", newline="\n")
            return f"wrote {args['path']} ({len(str(args['content']))} characters)", None
        if name == "edit_file":
            if not path.is_file():
                return f"ERROR: no such file: {args['path']}", None
            text = path.read_text(encoding="utf-8", errors="replace")
            n = text.count(str(args["old_text"])) if args["old_text"] else 0
            if n != 1:
                return (f"ERROR: old_text occurs {n} times in {args['path']}; it must occur exactly once. "
                        "Read the file again and copy the text exactly, with more surrounding lines if needed."), None
            path.write_text(text.replace(str(args["old_text"]), str(args["new_text"]), 1), encoding="utf-8", newline="\n")
            return f"edited {args['path']}", None
        raise AssertionError(name)


def run_project_tests(root: Path, lang: str, machine_tools: dict, file: str | None = None) -> tuple[int | None, str]:
    """Run the project's test file (or another file of the project) inside the sandbox.
    Raises `Blocked` if the OS refuses to start it."""
    test = file or TEST_FILE[lang]
    if lang == "js":
        return _run([machine_tools["node"], "--permission", f"--allow-fs-read={root}", test], str(root), DEFAULT_TIMEOUT_S)
    # Python: the launcher lives outside the project folder, installs the audit hook, then runs the test file.
    with tempfile.TemporaryDirectory(prefix="lab-agent-launch-") as tmp:
        launcher = Path(tmp, "launch.py")
        launcher.write_text(
            PY_GUARD + "import runpy\n_sys.path.insert(0, _os.getcwd())\n"
            f"runpy.run_path({test!r}, run_name='__main__')\n", encoding="utf-8")
        return _run([machine_tools["python"], "-I", "-X", "utf8", str(launcher)], str(root), DEFAULT_TIMEOUT_S)


def write_files(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- grading

def grade_repo(task: AgentTask, workspace: Path, machine_tools: dict) -> tuple[CheckResult, float | None]:
    """Copy the project, put the hidden tests over it, run them. Only the result counts.
    Returns the pass/fail result and a score from 0 to 1: the share of rule groups that pass when
    the hidden test file prints `RESULT passed/total`, else 1 or 0."""
    with tempfile.TemporaryDirectory(prefix="lab-agent-grade-") as tmp:
        copy = Path(tmp, "project")
        shutil.copytree(workspace, copy, ignore=shutil.ignore_patterns("__pycache__"))
        write_files(copy, task.spec["hidden"])
        try:
            code, out = run_project_tests(copy.resolve(), task.spec["lang"], machine_tools)
        except Blocked as e:
            return CheckResult(None, str(e)), None
    counted = RESULT_RE.search(out)
    score = int(counted[1]) / int(counted[2]) if counted and int(counted[2]) else float(code == 0)
    return CheckResult(code == 0, out[-900:] if code != 0 else (counted[0] if counted else "hidden tests pass")), score


def _contains_all(text: str, items: list) -> list:
    low = text.casefold()
    return [i for i in items if not any(str(o).casefold() in low for o in (i if isinstance(i, list) else [i]))]


def grade_tool(task: AgentTask, calls: list[dict], final: str, bad: list[str]) -> CheckResult:
    """`calls` = [{"name", "args"}] in the order the model made them."""
    ex = task.spec["expect"]
    if bad:
        return CheckResult(False, "bad tool call: " + "; ".join(bad[:3]))
    names = [c["name"] for c in calls]
    if used := [n for n in ex.get("forbid", []) if n in names]:
        return CheckResult(False, f"called a tool it should not use: {used}")
    if len(calls) > ex.get("max_calls", 10**6):
        return CheckResult(False, f"{len(calls)} tool calls, at most {ex['max_calls']} allowed: {names}")
    if len(calls) < ex.get("min_calls", 0):
        return CheckResult(False, f"{len(calls)} tool calls, at least {ex['min_calls']} needed: {names}")
    pos = -1
    for want in ex.get("calls", []):
        hit = next((i for i, c in enumerate(calls)
                    if (i > pos or not ex.get("ordered")) and c["name"] == want["tool"]
                    and matches(want.get("args", {}), c["args"])), None)
        if hit is None:
            got = [(c["name"], c["args"]) for c in calls]
            return CheckResult(False, f"no call matches {want}; calls made: {json.dumps(got, ensure_ascii=False)[:500]}")
        pos = hit
    if missing := _contains_all(final, ex.get("final_contains", [])):
        return CheckResult(False, f"final answer lacks {missing}: {final[:200]!r}")
    if present := [x for x in ex.get("final_not_contains", []) if str(x).casefold() in final.casefold()]:
        return CheckResult(False, f"final answer must not contain {present}: {final[:200]!r}")
    for p in ex.get("final_regex", []):
        if not re.search(p, final, re.S | re.I):
            return CheckResult(False, f"final answer does not match {p!r}: {final[:200]!r}")
    return CheckResult(True, f"{len(calls)} call(s), final answer accepted")


# ---------------------------------------------------------------- the loop

def run_task(base_url: str, cfg: RunConfig, task: AgentTask, executor) -> dict:
    """Model turn -> execute its tool calls -> feed the results back, until the model answers
    without a tool call or a limit is reached."""
    messages: list[dict] = [{"role": "system", "content": task.system}, {"role": "user", "content": task.prompt}]
    names = {t["function"]["name"] for t in task.tools}
    calls: list[dict] = []
    bad: list[str] = []
    turns: list[dict] = []
    final, finish = "", "max_steps"
    t0 = time.perf_counter()
    for _ in range(task.max_steps):
        turn = client.chat_turn(base_url, messages, tools=task.tools, thinking=cfg.thinking,
                                sampling=cfg.sampling, max_tokens=cfg.max_tokens,
                                timeout_s=cfg.request_timeout_s)
        turns.append({"prompt_tokens": turn.prompt_tokens, "cached_tokens": turn.cached_tokens,
                      "completion_tokens": turn.completion_tokens, "thinking_tokens": turn.thinking_tokens,
                      "wall_s": turn.wall_s, "decode_tok_s": turn.decode_tok_s,
                      "finish_reason": turn.finish_reason, "reasoning": turn.reasoning})
        if turn.error:
            overflow = "context" in turn.error.lower() and ("exceed" in turn.error.lower() or "too large" in turn.error.lower())
            final, finish = turn.error, "context_overflow" if overflow else "error"
            break
        if not turn.tool_calls:
            final = turn.content
            finish = "cut_off" if turn.finish_reason == "length" else ("final" if turn.content.strip() else "empty")
            break
        echoed = []
        results = []
        for n, call in enumerate(turn.tool_calls):
            call_id = call["id"] or f"call_{len(calls)}_{n}"
            try:
                args = json.loads(call["arguments"] or "{}")
            except json.JSONDecodeError:
                args = None
            if not isinstance(args, dict):
                text, why = "ERROR: the arguments were not a valid JSON object.", f"{call['name']}: arguments not valid JSON"
                args = None
            elif call["name"] not in names:
                text, why = (f"ERROR: there is no tool named {call['name']!r}. Available tools: {', '.join(sorted(names))}.",
                             f"unknown tool {call['name']!r}")
            else:
                text, why = executor.call(call["name"], args)
            if why:
                bad.append(why)
            if len(text) > RESULT_CHARS:
                text = text[:RESULT_CHARS] + f"\n[... cut: {len(text) - RESULT_CHARS} more characters]"
            calls.append({"name": call["name"], "args": args, "raw": None if args is not None else call["arguments"][:300]})
            echoed.append({"id": call_id, "type": "function",
                           "function": {"name": call["name"], "arguments": json.dumps(args or {}, ensure_ascii=False)}})
            results.append({"role": "tool", "tool_call_id": call_id, "content": text})
        messages.append({"role": "assistant", "content": turn.content or "", "tool_calls": echoed})
        messages += results
        if turn.finish_reason == "length":
            finish = "cut_off"
            break
        if time.perf_counter() - t0 > TASK_WALL_S:
            finish = "timeout"
            break
    return {"messages": messages, "turns": turns, "calls": calls, "bad": bad, "final": final, "finish": finish,
            "wall_s": round(time.perf_counter() - t0, 1)}


def _sum(turns: list[dict], key: str) -> int:
    return sum(t[key] or 0 for t in turns)


def execute(base_url: str, cfg: RunConfig, task: AgentTask, machine: Machine) -> tuple[dict, CheckResult, float | None]:
    """Run one task. Returns the loop record, pass/fail, and a score from 0 to 1."""
    if task.kind == "tool":
        out = run_task(base_url, cfg, task, MockTools(task))
        chk = grade_tool(task, out["calls"], out["final"], out["bad"])
        return out, chk, float(bool(chk.passed))
    with tempfile.TemporaryDirectory(prefix="lab-agent-") as tmp:
        root = Path(tmp).resolve() / "project"
        root.mkdir()
        write_files(root, task.spec["files"])
        _, start = grade_repo(task, root, machine.tools)   # what the untouched project already scores
        out = run_task(base_url, cfg, task, Workspace(root, task.spec["lang"], machine.tools))
        out["score_start"] = start
        chk, score = grade_repo(task, root, machine.tools)
        return out, chk, score


# ---------------------------------------------------------------- runner

def run_key(row: dict) -> tuple:
    return (row["machine"], row["config"], row["config_hash"], row["task"], row["task_hash"],
            row["repeat"], row.get("agent_version"))


def load_rows(path: Path = AGENT_RUNS) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_agent_config(cfg: RunConfig, tasks: list[AgentTask], machine: Machine, repeats: int,
                     dry_run: bool = False) -> None:
    done = {run_key(r) for r in load_rows()}
    todo = [(t, r) for r in range(repeats) for t in tasks
            if (machine.name, cfg.name, cfg.config_hash, t.id, t.task_hash, r, AGENT_VERSION) not in done]
    print(f"\n== {cfg.name}  (hash {cfg.config_hash}, machine {machine.name}, thinking {'on' if cfg.thinking else 'off'})")
    print(f"   model {cfg.model}  [{cfg.model_bytes / 1e9:.2f} GB]")
    print(f"   {len(todo)} agent runs to do, {len(tasks) * repeats - len(todo)} of {len(tasks) * repeats} "
          f"already in {AGENT_RUNS.name}", flush=True)
    cmd = cfg.server_command(machine)
    if dry_run:
        print("   server:", " ".join(cmd))
        for t, r in todo:
            print(f"   would run {t.id} r{r}")
        return
    if not todo:
        return
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    passed = graded = 0
    with LlamaServer(cmd, machine.base_url, machine.host, machine.port, cfg.model,
                     LOG_DIR / f"agent__{cfg.name}__{stamp}.log", machine.health_timeout_s) as srv:
        info = srv.info
        print(f"   server up in {info['load_s']}s, build {info.get('build')}, "
              f"buffers {json.dumps(info['buffers_mib'])}", flush=True)
        for i, (task, r) in enumerate(todo, 1):
            started = datetime.now().astimezone().isoformat(timespec="seconds")
            out, chk, score = execute(machine.base_url, cfg, task, machine)
            turns = out["turns"]
            speeds = [t["decode_tok_s"] for t in turns if t["decode_tok_s"]]
            row = {
                "ts": started, "machine": machine.name, "config": cfg.name, "config_hash": cfg.config_hash,
                "agent_version": AGENT_VERSION, "task": task.id, "task_hash": task.task_hash, "repeat": r,
                "kind": task.kind, "category": task.category,
                "passed": chk.passed, "score": score, "score_start": out.get("score_start"),
                "check_detail": chk.detail, "finish": out["finish"],
                "steps": len(turns), "n_calls": len(out["calls"]), "bad_calls": out["bad"],
                "calls": [{"name": c["name"], "args": _short(c["args"])} for c in out["calls"]],
                "final": out["final"][:1500],
                "prompt_tokens_first": turns[0]["prompt_tokens"] if turns else None,
                "prompt_tokens_max": max((t["prompt_tokens"] or 0 for t in turns), default=0),
                "completion_tokens": _sum(turns, "completion_tokens"),
                "thinking_tokens": _sum(turns, "thinking_tokens"),
                "model_s": round(sum(t["wall_s"] for t in turns), 1), "wall_s": out["wall_s"],
                "decode_tok_s": round(statistics.median(speeds), 1) if speeds else None,
                "model_file": cfg.model.name, "model_bytes": cfg.model_bytes, "backend": cfg.backend.name,
                "ctx": cfg.ctx, "thinking": cfg.thinking, "sampling_preset": cfg.sampling_preset,
                "sampling": cfg.sampling, "max_tokens": cfg.max_tokens,
                "server": {**info, "cmd": cmd},
            }
            append_row(row, AGENT_RUNS)
            log = TRANSCRIPT_DIR / cfg.name / f"{task.id}__r{r}__{stamp}.json"
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text(json.dumps({"task": task.id, "passed": chk.passed, "detail": chk.detail,
                                       "finish": out["finish"], "messages": out["messages"], "turns": turns},
                                      ensure_ascii=False, indent=1), encoding="utf-8")
            if chk.passed is not None:
                graded += 1
                passed += chk.passed
            verdict = {True: "PASS", False: "FAIL", None: "NOT GRADED"}[chk.passed]
            if task.kind == "repo" and score is not None:
                verdict = f"{verdict} {score:4.0%}"
            print(f"   [{i:>3}/{len(todo)}] {task.id:<26} r{r} {verdict:<11} {out['wall_s']:6.1f}s  "
                  f"steps {len(turns):>2}  calls {len(out['calls']):>2}  bad {len(out['bad'])}  "
                  f"ctx {row['prompt_tokens_max']:>5}  think {row['thinking_tokens']:>5}  {out['finish']}", flush=True)
            if out["finish"] == "error" and not srv.alive():
                raise ServerError(f"llama-server died during {task.id}; log tail:\n{srv.log_tail()}")
        memory = srv.memory()   # after the work: the mapped file has settled
        if memory:
            append_row({"ts": datetime.now().astimezone().isoformat(timespec="seconds"), "machine": machine.name,
                        "config": cfg.name, "config_hash": cfg.config_hash, "mode": "agent", "ctx": cfg.ctx,
                        "model_file": cfg.model.name, "model_bytes": cfg.model_bytes, "runs": len(todo),
                        "buffers_mib": info["buffers_mib"], **memory}, MEMORY_FILE)
            print(f"   memory: server {memory.get('working_set_gib')} GiB in RAM ({memory.get('private_gib')} GiB private), "
                  f"{memory.get('system_available_gib')} GiB of RAM left for other programs "
                  f"({memory.get('system_available_before_gib')} before the model), GPU {memory.get('gpu_used_mib')} MiB in use")
    print(f"   done: {passed}/{graded} agent runs passed this session")


def _short(args: dict | None) -> dict | None:
    """Arguments for the results file: long strings (file contents) are cut."""
    if args is None:
        return None
    return {k: (v[:200] + f"... [{len(v)} chars]" if isinstance(v, str) and len(v) > 200 else v) for k, v in args.items()}


# ---------------------------------------------------------------- selftest

def selftest(tasks: list[AgentTask], machine: Machine) -> int:
    """Prove the graders before any model is judged.
    tool task: its `reference` transcript must pass, its `wrong` one must fail, and the reference
    calls must be accepted by the scripted tools. repo task: the untouched project must fail the
    visible and the hidden tests; with the `reference` files written, both must pass."""
    problems = 0
    for t in tasks:
        notes: list[str] = []
        before = problems
        try:
            if t.kind == "tool":
                tools = MockTools(t)
                for label, script, should_pass in (("reference", t.reference, True), ("wrong", t.wrong, False)):
                    if script is None:
                        continue
                    calls = [{"name": c["tool"], "args": c.get("args", {})} for c in script.get("calls", [])]
                    bad = [f"unknown tool {c['name']!r}" for c in calls if c["name"] not in tools.defs]
                    bad += [why for c in calls if c["name"] in tools.defs for _, why in [tools.call(c["name"], c["args"])] if why]
                    res = grade_tool(t, calls, script.get("final", ""), bad)
                    ok = res.passed == should_pass
                    problems += not ok
                    notes.append(f"{label} {'passes' if res.passed else 'is caught'}" if ok else
                                 f"{label} {'FAILS' if should_pass else 'PASSES (grader too weak)'}: {res.detail}")
            else:
                with tempfile.TemporaryDirectory(prefix="lab-agent-self-") as tmp:
                    root = Path(tmp).resolve() / "project"
                    root.mkdir()
                    write_files(root, t.spec["files"])
                    vis_code, _ = run_project_tests(root, t.spec["lang"], machine.tools)
                    hid, hid_score = grade_repo(t, root, machine.tools)
                    write_files(root, t.reference or {})
                    ref_code, ref_out = run_project_tests(root, t.spec["lang"], machine.tools)
                    ref, ref_score = grade_repo(t, root, machine.tools)
                # A task may start with passing visible tests on purpose (a bug report in words, no failing test).
                start = ("untouched project passes its visible tests (by design)" if t.spec.get("visible_pass")
                         else "untouched project fails its tests")
                for label, bad_when, detail in (
                        (start, (vis_code == 0) != bool(t.spec.get("visible_pass")),
                         f"visible tests on the untouched project: exit code {vis_code}, not as the task says"),
                        (f"untouched project scores {hid_score:.0%} on the hidden tests", hid.passed is not False,
                         "hidden tests do not fail on the untouched project"),
                        ("reference passes its tests", ref_code != 0, f"visible tests FAIL with the reference:\n{ref_out[-500:]}"),
                        ("reference passes the hidden tests", ref.passed is not True or ref_score != 1.0,
                         f"hidden tests FAIL with the reference:\n{ref.detail}")):
                    problems += bad_when
                    notes.append(detail if bad_when else label)
        except Blocked as e:
            notes.append(f"NOT GRADED ({e})")
        print(f"{'BAD' if problems > before else 'ok':>6}  {t.id:<26} " + "; ".join(notes))
    print(f"\n{problems} problem(s)")
    return 1 if problems else 0
