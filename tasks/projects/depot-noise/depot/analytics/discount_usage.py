"""How often each discount was given. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DiscountUseRecord:
    key: str
    times: int
    note: str = ""


def load_discount_uses(rows):
    """Build records from (key, times) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = DiscountUseRecord(str(key), int(value))
    return list(records.values())


def total_times(records):
    return sum(record.times for record in records)


def top_discount_uses(records, n):
    """The n records with the largest times; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.times, record.key))[:n]


def split_discount_uses(records, threshold=50):
    """Return (below, at_or_above) by times."""
    below = [record for record in records if record.times < threshold]
    return below, [record for record in records if record.times >= threshold]


def find_discount_use(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_discount_uses(records, percent):
    """A copy of the records with times changed by percent (rounded down)."""
    return [DiscountUseRecord(r.key, r.times + r.times * percent // 100, r.note) for r in records]


def merge_discount_uses(first, second):
    """Add the times of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = DiscountUseRecord(old.key, old.times + record.times, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_discount_uses(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.times < 0:
            problems.append(f"{record.key}: negative times")
    return problems


def summarise_discount_uses(records):
    values = sorted(record.times for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_discount_use_table(records, width=16):
    lines = [f"{'key':<{width}} {'times':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.times:>12}")
    lines.append(f"{'total':<{width}} {total_times(records):>12}")
    return "\n".join(lines) + "\n"
