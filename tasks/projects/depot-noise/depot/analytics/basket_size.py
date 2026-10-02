"""Units per order. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class BasketRecord:
    key: str
    units: int
    note: str = ""


def load_baskets(rows):
    """Build records from (key, units) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = BasketRecord(str(key), int(value))
    return list(records.values())


def total_units(records):
    return sum(record.units for record in records)


def top_baskets(records, n):
    """The n records with the largest units; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.units, record.key))[:n]


def split_baskets(records, threshold=40):
    """Return (below, at_or_above) by units."""
    below = [record for record in records if record.units < threshold]
    return below, [record for record in records if record.units >= threshold]


def find_basket(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_baskets(records, percent):
    """A copy of the records with units changed by percent (rounded down)."""
    return [BasketRecord(r.key, r.units + r.units * percent // 100, r.note) for r in records]


def merge_baskets(first, second):
    """Add the units of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = BasketRecord(old.key, old.units + record.units, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_baskets(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.units < 0:
            problems.append(f"{record.key}: negative units")
    return problems


def summarise_baskets(records):
    values = sorted(record.units for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_basket_table(records, width=15):
    lines = [f"{'key':<{width}} {'units':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.units:>12}")
    lines.append(f"{'total':<{width}} {total_units(records):>12}")
    return "\n".join(lines) + "\n"
