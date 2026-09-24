"""Grade a model answer against a task.

Safety rules for model-written code (LOCAL_LLM_LAB.md section 7):
- Python / JS / C++ run as a subprocess inside a fresh temp folder, with a timeout,
  a minimal environment and no stdin. Node also runs with its permission model on;
  Python gets an audit hook (PY_GUARD) that blocks writes outside the temp folder,
  subprocesses and sockets. Both guard against accidents; neither is a hard sandbox.
- SQL runs in an in-memory SQLite database with a read-only authorizer and a time limit,
  so it cannot touch any file.
- If Windows (Smart App Control) refuses to start a compiled test program, the run is
  recorded as not graded (passed = None), never as a model failure.
"""

import ast
import json
import math
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from .tasks import Task

DEFAULT_TIMEOUT_S = 10
COMPILE_TIMEOUT_S = 120
DETAIL_CHARS = 1500

FENCE_RE = re.compile(r"```[ \t]*([\w+#.-]*)[^\n]*\n(.*?)```", re.DOTALL)
LANG_ALIASES = {
    "python": "python", "py": "python", "python3": "python",
    "js": "js", "javascript": "js", "node": "js", "mjs": "js", "cjs": "js",
    "cpp": "cpp", "c++": "cpp", "cc": "cpp", "cxx": "cpp", "hpp": "cpp",
    "sql": "sql", "sqlite": "sql", "sqlite3": "sql",
    "json": "json",
}
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
WIN_APP_CONTROL_BLOCKED = 4551  # "An Application Control policy has blocked this file"

# Prepended to model Python code. Runs before any model code.
PY_GUARD = '''\
import os as _os, sys as _sys
_sys.dont_write_bytecode = True
def _lab_guard(event, args, _root=_os.path.realpath(_os.getcwd()) + _os.sep):
    def outside(p):
        return isinstance(p, (str, bytes, _os.PathLike)) and not (
            _os.path.realpath(_os.fsdecode(p)) + _os.sep).startswith(_root)
    if event == "open":
        path, mode, flags = (list(args) + [None, None, None])[:3]
        writes = _os.O_WRONLY | _os.O_RDWR | _os.O_CREAT | _os.O_APPEND | _os.O_TRUNC
        writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
            isinstance(flags, int) and flags & writes)
        if writing and outside(path):
            raise PermissionError(f"lab sandbox: writing outside the temp folder is blocked: {path!r}")
    elif event in ("os.remove", "os.rmdir", "os.rename", "os.replace", "os.mkdir",
                   "os.chmod", "os.truncate", "shutil.rmtree"):
        if args and outside(args[0]):
            raise PermissionError(f"lab sandbox: {event} outside the temp folder is blocked")
    elif event in ("subprocess.Popen", "os.system", "os.exec", "os.spawn", "os.posix_spawn",
                   "os.startfile", "socket.connect", "ctypes.dlopen"):
        raise PermissionError(f"lab sandbox: {event} is blocked")
_sys.addaudithook(_lab_guard)
del _lab_guard
# ---- model code ----
'''

if sys.platform == "win32":
    # Child processes inherit this: a crashing test program must not open a
    # "stopped working" dialog that would block the run until the timeout.
    import ctypes
    ctypes.windll.kernel32.SetErrorMode(0x0001 | 0x0002)  # FAILCRITICALERRORS | NOGPFAULTERRORBOX


@dataclass
class CheckResult:
    passed: bool | None  # None = needs manual grading
    detail: str = ""


class Blocked(Exception):
    """The OS refused to start a program (e.g. Smart App Control): cannot grade, not a failure."""


# ---------------------------------------------------------------- code extraction

def code_blocks(answer: str, lang: str) -> list[str]:
    """Fenced blocks in `lang`; else unlabelled blocks; else (no fences at all) the whole answer."""
    fences = [(LANG_ALIASES.get(tag.lower(), tag.lower()), body) for tag, body in FENCE_RE.findall(answer)]
    if not fences:
        return [answer.strip()] if answer.strip() else []
    same = [body for tag, body in fences if tag == lang]
    return same or [body for tag, body in fences if tag == ""]


def pick_block(blocks: list[str], entry_re: re.Pattern | None) -> str | None:
    """The first block that defines the entry point (models put the solution first and
    examples or 'alternative versions' after it); else the first block."""
    if not blocks:
        return None
    if entry_re:
        for block in blocks:
            if entry_re.search(block):
                return block
    return blocks[0]


def python_definitions_only(code: str) -> str:
    """Keep imports, functions, classes and assignments; drop the model's own example
    calls, prints and asserts, so a wrong example cannot fail a correct function."""
    tree = ast.parse(code)
    keep = (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
            ast.Assign, ast.AnnAssign, ast.TypeAlias)
    tree.body = [node for node in tree.body if isinstance(node, keep)]
    return ast.unparse(tree)


def strip_cpp_main(code: str) -> str:
    """Remove a model-written `int main(...) {...}` (the tests bring their own)."""
    m = re.search(r"\bint\s+main\s*\([^)]*\)\s*\{", code)
    if not m:
        return code
    depth, i = 1, m.end()
    while i < len(code) and depth:
        depth += {"{": 1, "}": -1}.get(code[i], 0)
        i += 1
    return code[:m.start()] + code[i:]


# ---------------------------------------------------------------- subprocess sandbox

def _env(tmp: str) -> dict[str, str]:
    keep = ("SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "PATH", "PATHEXT", "COMSPEC")
    env = {k: os.environ[k] for k in keep if k in os.environ}
    env.update(TEMP=tmp, TMP=tmp, HOME=tmp, USERPROFILE=tmp)
    return env


def _run(cmd: list[str], cwd: str, timeout_s: float) -> tuple[int | None, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, env=_env(cwd), stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return None, f"timeout after {timeout_s}s"
    except OSError as e:
        if getattr(e, "winerror", None) == WIN_APP_CONTROL_BLOCKED:
            raise Blocked(f"Windows Smart App Control blocked {Path(cmd[0]).name}; "
                          "not graded (grade by hand, or run where SAC is off)") from e
        return None, f"could not start {cmd[0]!r}: {e}"
    return p.returncode, (p.stdout + p.stderr)[-DETAIL_CHARS:]


def _result(code: int | None, output: str) -> CheckResult:
    if code == 0:
        return CheckResult(True, output[-300:])
    return CheckResult(False, output or f"exit code {code}")


# ---------------------------------------------------------------- checks

def check_python(task: Task, answer: str, tools: dict) -> CheckResult:
    entry = task.params.get("entry")
    entry_re = re.compile(rf"^\s*(?:async\s+def|def|class)\s+{entry}\b|^{entry}\s*[:=]", re.M) if entry else None
    block = pick_block(code_blocks(answer, "python"), entry_re)
    if block is None:
        return CheckResult(False, "no python code block found")
    try:
        code = python_definitions_only(block)
    except SyntaxError as e:
        return CheckResult(False, f"syntax error in answer: {e}")
    with tempfile.TemporaryDirectory(prefix="lab-py-") as tmp:
        Path(tmp, "check.py").write_text(f"{PY_GUARD}{code}\n\n# ---- tests ----\n{task.params['tests']}",
                                         encoding="utf-8")
        return _result(*_run([tools["python"], "-I", "-X", "utf8", "check.py"], tmp,
                             task.params.get("timeout_s", DEFAULT_TIMEOUT_S)))


def check_js(task: Task, answer: str, tools: dict) -> CheckResult:
    entry = task.params.get("entry")
    entry_re = re.compile(rf"\bfunction\s+{entry}\b|\b{entry}\s*=|\bclass\s+{entry}\b") if entry else None
    block = pick_block(code_blocks(answer, "js"), entry_re)
    if block is None:
        return CheckResult(False, "no javascript code block found")
    code = re.sub(r"^(\s*)export\s+(?:default\s+)?", r"\1", block, flags=re.M)  # ESM -> script
    tests = "{\nconst assert = require('node:assert/strict');\n" + task.params["tests"] + "\n}\n"
    with tempfile.TemporaryDirectory(prefix="lab-js-") as tmp:
        Path(tmp, "check.cjs").write_text(f"{code}\n;\n// ---- tests ----\n{tests}", encoding="utf-8")
        cmd = [tools["node"], "--permission", f"--allow-fs-read={tmp}", "check.cjs"]
        return _result(*_run(cmd, tmp, task.params.get("timeout_s", DEFAULT_TIMEOUT_S)))


def check_cpp(task: Task, answer: str, tools: dict) -> CheckResult:
    entry = task.params.get("entry")
    entry_re = re.compile(rf"\b{entry}\s*\(") if entry else None
    block = pick_block(code_blocks(answer, "cpp"), entry_re)
    if block is None:
        return CheckResult(False, "no c++ code block found")
    with tempfile.TemporaryDirectory(prefix="lab-cpp-") as tmp:
        Path(tmp, "check.cpp").write_text(
            f"{strip_cpp_main(block)}\n\n// ---- tests ----\n{task.params['tests']}", encoding="utf-8")
        exe = str(Path(tmp, "check.exe"))
        code, out = _run([tools["cxx"], "-std=c++20", "-O1", "-static", "-o", exe, "check.cpp"],
                         tmp, COMPILE_TIMEOUT_S)
        if code != 0:
            return CheckResult(False, f"compile failed:\n{out}")
        return _result(*_run([exe], tmp, task.params.get("timeout_s", DEFAULT_TIMEOUT_S)))


def _read_only(action: int, *_args) -> int:
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION,
               sqlite3.SQLITE_RECURSIVE}
    return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY


def _norm_row(row: tuple) -> tuple:
    out = []
    for v in row:
        if isinstance(v, float):
            v = round(v, 6)
            if v.is_integer():
                v = int(v)
        out.append(v)
    return tuple(out)


def check_sql(task: Task, answer: str, fixtures: dict) -> CheckResult:
    blocks = code_blocks(answer, "sql")
    if not blocks:
        return CheckResult(False, "no sql found")
    query = blocks[0].strip().rstrip(";").strip()
    fx = fixtures[task.params["fixture"]]
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(f"{fx['ddl']}\n{fx['data']}")
        expected = [_norm_row(r) for r in conn.execute(task.params["expected_sql"]).fetchall()]
        conn.set_authorizer(_read_only)
        deadline = time.perf_counter() + task.params.get("timeout_s", DEFAULT_TIMEOUT_S)
        conn.set_progress_handler(lambda: int(time.perf_counter() > deadline), 10_000)
        try:
            cur = conn.execute(query)
            got = [_norm_row(r) for r in cur.fetchall()]
        except sqlite3.Error as e:
            return CheckResult(False, f"SQL error: {e}")
    finally:
        conn.close()
    if not task.params.get("ordered", False):
        expected, got = sorted(expected, key=repr), sorted(got, key=repr)
    if got == expected:
        return CheckResult(True, f"{len(got)} rows match")
    return CheckResult(False, f"expected {expected[:10]}\ngot      {got[:10]}")


def _norm_text(s: str) -> str:
    s = s.strip().strip("`*_ \"'").strip().rstrip(".").strip()
    return " ".join(s.split()).casefold()


def check_exact(task: Task, answer: str) -> CheckResult:
    text = answer
    if pattern := task.params.get("extract"):
        found = re.findall(pattern, answer, re.I | re.M)
        if not found:
            return CheckResult(False, f"no match for extract pattern {pattern!r}")
        text = found[-1]
    expected = task.params["expected"]
    for e in expected if isinstance(expected, list) else [expected]:
        if isinstance(e, (int, float)):
            nums = NUMBER_RE.findall(text.replace(",", ""))
            if nums and math.isclose(float(nums[-1]), float(e)):
                return CheckResult(True, text.strip()[:200])
        elif _norm_text(text) == _norm_text(str(e)):
            return CheckResult(True, text.strip()[:200])
    return CheckResult(False, f"expected {expected!r}, got {text.strip()[:200]!r}")


def check_contains(task: Task, answer: str) -> CheckResult:
    """Every `include` item must appear (an item that is a list = any one of them);
    no `exclude` item may appear. Case-insensitive."""
    low = answer.casefold()
    missing = []
    for item in task.params["include"]:
        options = item if isinstance(item, list) else [item]
        if not any(str(o).casefold() in low for o in options):
            missing.append(options)
    present = [x for x in task.params.get("exclude", []) if str(x).casefold() in low]
    if missing or present:
        return CheckResult(False, f"missing: {missing}; must not appear: {present}")
    return CheckResult(True, "all key facts present")


def check_regex(task: Task, answer: str) -> CheckResult:
    text = answer.strip()
    full = task.params.get("fullmatch", False)
    for p in task.params["patterns"]:
        hit = re.fullmatch(p, text, re.M) if full else re.search(p, text, re.M)
        if not hit:
            return CheckResult(False, f"pattern not matched: {p!r}")
    for p in task.params.get("not_patterns", []):
        if m := re.search(p, text, re.M):
            return CheckResult(False, f"forbidden pattern {p!r} matched {m.group(0)!r}")
    return CheckResult(True, "all patterns matched")


def check_json(task: Task, answer: str) -> CheckResult:
    try:
        got = json.loads(answer.strip())
    except json.JSONDecodeError as e:
        return CheckResult(False, f"not valid JSON on its own ({e}); answer starts {answer.strip()[:80]!r}")
    if got == task.params["expected"]:
        return CheckResult(True, "JSON matches")
    return CheckResult(False, f"expected {task.params['expected']}\ngot      {got}")


def run_check(task: Task, answer: str, tools: dict, fixtures: dict) -> CheckResult:
    try:
        return _dispatch(task, answer, tools, fixtures)
    except Blocked as e:
        return CheckResult(None, str(e))


def _dispatch(task: Task, answer: str, tools: dict, fixtures: dict) -> CheckResult:
    match task.check:
        case "python_tests":
            return check_python(task, answer, tools)
        case "js_tests":
            return check_js(task, answer, tools)
        case "cpp_tests":
            return check_cpp(task, answer, tools)
        case "sql_result":
            return check_sql(task, answer, fixtures)
        case "exact":
            return check_exact(task, answer)
        case "contains":
            return check_contains(task, answer)
        case "regex":
            return check_regex(task, answer)
        case "json_match":
            return check_json(task, answer)
        case "manual":
            return CheckResult(None, "needs manual grading")
    raise ValueError(f"unknown check {task.check!r}")
