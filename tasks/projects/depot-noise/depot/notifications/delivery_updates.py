"""Delivery update messages. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateRecord:
    key: str
    delay_days: int
    note: str = ""


def load_updates(rows):
    """Build records from (key, delay_days) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = UpdateRecord(str(key), int(value))
    return list(records.values())


def total_delay_days(records):
    return sum(record.delay_days for record in records)


def top_updates(records, n):
    """The n records with the largest delay_days; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.delay_days, record.key))[:n]


def split_updates(records, threshold=40):
    """Return (below, at_or_above) by delay_days."""
    below = [record for record in records if record.delay_days < threshold]
    return below, [record for record in records if record.delay_days >= threshold]


def find_update(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_updates(records, percent):
    """A copy of the records with delay_days changed by percent (rounded down)."""
    return [UpdateRecord(r.key, r.delay_days + r.delay_days * percent // 100, r.note) for r in records]


def merge_updates(first, second):
    """Add the delay_days of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = UpdateRecord(old.key, old.delay_days + record.delay_days, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_updates(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.delay_days < 0:
            problems.append(f"{record.key}: negative delay_days")
    return problems


def summarise_updates(records):
    values = sorted(record.delay_days for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_update_table(records, width=18):
    lines = [f"{'key':<{width}} {'delay_days':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.delay_days:>12}")
    lines.append(f"{'total':<{width}} {total_delay_days(records):>12}")
    return "\n".join(lines) + "\n"
