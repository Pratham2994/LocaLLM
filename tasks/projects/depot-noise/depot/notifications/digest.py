"""Daily digest for the team. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DigestItemRecord:
    key: str
    priority: int
    note: str = ""


def load_digest_items(rows):
    """Build records from (key, priority) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = DigestItemRecord(str(key), int(value))
    return list(records.values())


def total_priority(records):
    return sum(record.priority for record in records)


def top_digest_items(records, n):
    """The n records with the largest priority; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.priority, record.key))[:n]


def split_digest_items(records, threshold=30):
    """Return (below, at_or_above) by priority."""
    below = [record for record in records if record.priority < threshold]
    return below, [record for record in records if record.priority >= threshold]


def find_digest_item(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_digest_items(records, percent):
    """A copy of the records with priority changed by percent (rounded down)."""
    return [DigestItemRecord(r.key, r.priority + r.priority * percent // 100, r.note) for r in records]


def merge_digest_items(first, second):
    """Add the priority of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = DigestItemRecord(old.key, old.priority + record.priority, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_digest_items(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.priority < 0:
            problems.append(f"{record.key}: negative priority")
    return problems


def summarise_digest_items(records):
    values = sorted(record.priority for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_digest_item_table(records, width=17):
    lines = [f"{'key':<{width}} {'priority':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.priority:>12}")
    lines.append(f"{'total':<{width}} {total_priority(records):>12}")
    return "\n".join(lines) + "\n"
