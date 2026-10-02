"""Loading dock slots. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DockSlotRecord:
    key: str
    minutes: int
    note: str = ""


def load_dock_slots(rows):
    """Build records from (key, minutes) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = DockSlotRecord(str(key), int(value))
    return list(records.values())


def total_minutes(records):
    return sum(record.minutes for record in records)


def top_dock_slots(records, n):
    """The n records with the largest minutes; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.minutes, record.key))[:n]


def split_dock_slots(records, threshold=50):
    """Return (below, at_or_above) by minutes."""
    below = [record for record in records if record.minutes < threshold]
    return below, [record for record in records if record.minutes >= threshold]


def find_dock_slot(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_dock_slots(records, percent):
    """A copy of the records with minutes changed by percent (rounded down)."""
    return [DockSlotRecord(r.key, r.minutes + r.minutes * percent // 100, r.note) for r in records]


def merge_dock_slots(first, second):
    """Add the minutes of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = DockSlotRecord(old.key, old.minutes + record.minutes, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_dock_slots(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.minutes < 0:
            problems.append(f"{record.key}: negative minutes")
    return problems


def summarise_dock_slots(records):
    values = sorted(record.minutes for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_dock_slot_table(records, width=17):
    lines = [f"{'key':<{width}} {'minutes':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.minutes:>12}")
    lines.append(f"{'total':<{width}} {total_minutes(records):>12}")
    return "\n".join(lines) + "\n"
