"""Orders that came after their estimate. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class LateDeliveryRecord:
    key: str
    days_late: int
    note: str = ""


def load_late_deliveries(rows):
    """Build records from (key, days_late) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = LateDeliveryRecord(str(key), int(value))
    return list(records.values())


def total_days_late(records):
    return sum(record.days_late for record in records)


def top_late_deliveries(records, n):
    """The n records with the largest days_late; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.days_late, record.key))[:n]


def split_late_deliveries(records, threshold=20):
    """Return (below, at_or_above) by days_late."""
    below = [record for record in records if record.days_late < threshold]
    return below, [record for record in records if record.days_late >= threshold]


def find_late_delivery(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_late_deliveries(records, percent):
    """A copy of the records with days_late changed by percent (rounded down)."""
    return [LateDeliveryRecord(r.key, r.days_late + r.days_late * percent // 100, r.note) for r in records]


def merge_late_deliveries(first, second):
    """Add the days_late of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = LateDeliveryRecord(old.key, old.days_late + record.days_late, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_late_deliveries(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.days_late < 0:
            problems.append(f"{record.key}: negative days_late")
    return problems


def summarise_late_deliveries(records):
    values = sorted(record.days_late for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_late_delivery_table(records, width=20):
    lines = [f"{'key':<{width}} {'days_late':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.days_late:>12}")
    lines.append(f"{'total':<{width}} {total_days_late(records):>12}")
    return "\n".join(lines) + "\n"
