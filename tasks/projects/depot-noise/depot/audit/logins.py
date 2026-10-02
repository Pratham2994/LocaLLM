"""Log of staff logins. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class LoginCountRecord:
    key: str
    logins: int
    note: str = ""


def load_login_counts(rows):
    """Build records from (key, logins) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = LoginCountRecord(str(key), int(value))
    return list(records.values())


def total_logins(records):
    return sum(record.logins for record in records)


def top_login_counts(records, n):
    """The n records with the largest logins; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.logins, record.key))[:n]


def split_login_counts(records, threshold=70):
    """Return (below, at_or_above) by logins."""
    below = [record for record in records if record.logins < threshold]
    return below, [record for record in records if record.logins >= threshold]


def find_login_count(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_login_counts(records, percent):
    """A copy of the records with logins changed by percent (rounded down)."""
    return [LoginCountRecord(r.key, r.logins + r.logins * percent // 100, r.note) for r in records]


def merge_login_counts(first, second):
    """Add the logins of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = LoginCountRecord(old.key, old.logins + record.logins, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_login_counts(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.logins < 0:
            problems.append(f"{record.key}: negative logins")
    return problems


def summarise_login_counts(records):
    values = sorted(record.logins for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_login_count_table(records, width=12):
    lines = [f"{'key':<{width}} {'logins':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.logins:>12}")
    lines.append(f"{'total':<{width}} {total_logins(records):>12}")
    return "\n".join(lines) + "\n"
