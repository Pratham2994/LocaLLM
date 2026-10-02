"""Log of edited orders. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderEditRecord:
    key: str
    changes: int
    note: str = ""


def load_order_edits(rows):
    """Build records from (key, changes) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = OrderEditRecord(str(key), int(value))
    return list(records.values())


def total_changes(records):
    return sum(record.changes for record in records)


def top_order_edits(records, n):
    """The n records with the largest changes; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.changes, record.key))[:n]


def split_order_edits(records, threshold=10):
    """Return (below, at_or_above) by changes."""
    below = [record for record in records if record.changes < threshold]
    return below, [record for record in records if record.changes >= threshold]


def find_order_edit(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_order_edits(records, percent):
    """A copy of the records with changes changed by percent (rounded down)."""
    return [OrderEditRecord(r.key, r.changes + r.changes * percent // 100, r.note) for r in records]


def merge_order_edits(first, second):
    """Add the changes of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = OrderEditRecord(old.key, old.changes + record.changes, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_order_edits(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.changes < 0:
            problems.append(f"{record.key}: negative changes")
    return problems


def summarise_order_edits(records):
    values = sorted(record.changes for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_order_edit_table(records, width=13):
    lines = [f"{'key':<{width}} {'changes':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.changes:>12}")
    lines.append(f"{'total':<{width}} {total_changes(records):>12}")
    return "\n".join(lines) + "\n"
