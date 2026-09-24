"""Load and validate tasks/tasks.yaml."""

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from .config import ROOT, ConfigError, check_keys, read_yaml

TASKS_FILE = ROOT / "tasks" / "tasks.yaml"

# check type -> (required fields, optional fields)
CHECK_FIELDS: dict[str, tuple[set[str], set[str]]] = {
    "exact": ({"expected"}, {"extract"}),
    "contains": ({"include"}, {"exclude"}),
    "regex": ({"patterns"}, {"not_patterns", "fullmatch"}),
    "json_match": ({"expected"}, set()),
    "python_tests": ({"tests"}, {"entry", "timeout_s"}),
    "js_tests": ({"tests"}, {"entry", "timeout_s"}),
    "cpp_tests": ({"tests"}, {"entry", "timeout_s"}),
    "sql_result": ({"fixture", "expected_sql"}, {"ordered", "timeout_s"}),
    "manual": (set(), set()),
}
LANG_OF_CHECK = {"python_tests": "python", "js_tests": "js", "cpp_tests": "cpp", "sql_result": "sql"}
COMMON_REQUIRED = {"id", "category", "prompt", "check", "thinking"}
COMMON_OPTIONAL = {"reference", "wrong", "notes", "lang"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


@dataclass(frozen=True)
class Task:
    id: str
    category: str
    prompt: str
    check: str
    thinking: str  # "off" | "on" | "both"
    lang: str
    params: dict = field(default_factory=dict)  # check-specific fields
    reference: str | None = None  # a known-good answer: `lab selftest` must pass it
    wrong: str | None = None      # a known-bad answer: `lab selftest` must fail it
    notes: str | None = None

    @property
    def prompt_hash(self) -> str:
        """Hash of exactly what the model sees. Editing a prompt makes old results stale."""
        return hashlib.sha256(self.prompt.encode()).hexdigest()[:12]

    def runs_with(self, thinking: bool) -> bool:
        return self.thinking == "both" or self.thinking == ("on" if thinking else "off")


@dataclass(frozen=True)
class TaskSet:
    tasks: list[Task]
    fixtures: dict[str, dict[str, str]]  # name -> {"ddl": ..., "data": ...}

    def select(self, patterns: list[str] | None) -> list[Task]:
        from fnmatch import fnmatch
        if not patterns:
            return list(self.tasks)
        chosen = [t for t in self.tasks if any(fnmatch(t.id, p) for p in patterns)]
        if not chosen:
            raise ConfigError(f"no task matches {patterns}")
        return chosen


def _thinking(value: object, where: str) -> str:
    # YAML 1.1 reads bare on/off as booleans, so accept both spellings.
    if value is True:
        return "on"
    if value is False:
        return "off"
    if isinstance(value, str) and value.lower() in {"on", "off", "both"}:
        return value.lower()
    raise ConfigError(f"{where}: thinking must be on, off or both")


def load_tasks(path: Path = TASKS_FILE) -> TaskSet:
    data = read_yaml(path)
    check_keys(str(path), data, {"tasks"}, {"fixtures"})
    fixtures = {}
    for name, fx in (data.get("fixtures") or {}).items():
        check_keys(f"{path}: fixtures.{name}", fx, {"ddl", "data"}, set())
        fixtures[name] = {"ddl": fx["ddl"].strip(), "data": fx["data"].strip()}

    tasks, seen = [], set()
    for i, raw in enumerate(data["tasks"]):
        where = f"{path}: task #{i + 1} ({raw.get('id', '?')})"
        check = raw.get("check")
        if check not in CHECK_FIELDS:
            raise ConfigError(f"{where}: check must be one of {sorted(CHECK_FIELDS)}")
        required, optional = CHECK_FIELDS[check]
        check_keys(where, raw, COMMON_REQUIRED | required, COMMON_OPTIONAL | optional)
        if not ID_RE.match(raw["id"]) or raw["id"] in seen:
            raise ConfigError(f"{where}: id must be unique, lowercase letters, digits and hyphens")
        seen.add(raw["id"])

        prompt = raw["prompt"].strip()
        if check == "sql_result":
            if raw["fixture"] not in fixtures:
                raise ConfigError(f"{where}: unknown fixture {raw['fixture']!r}")
            prompt = prompt.replace("{{ddl}}", fixtures[raw["fixture"]]["ddl"])
        if "{{" in prompt:
            raise ConfigError(f"{where}: prompt has an unfilled {{{{...}}}} placeholder")
        if check != "manual" and not raw.get("reference"):
            raise ConfigError(f"{where}: auto-checked tasks need a `reference` answer")

        tasks.append(Task(
            id=raw["id"],
            category=raw["category"],
            prompt=prompt,
            check=check,
            thinking=_thinking(raw["thinking"], where),
            lang=raw.get("lang") or LANG_OF_CHECK.get(check, "text"),
            params={k: raw[k] for k in required | optional if k in raw},
            reference=raw.get("reference"),
            wrong=raw.get("wrong"),
            notes=raw.get("notes"),
        ))
    return TaskSet(tasks, fixtures)
