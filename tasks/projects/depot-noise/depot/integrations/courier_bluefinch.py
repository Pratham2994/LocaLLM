"""Adapter for the Bluefinch courier. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ParcelRecord:
    key: str
    weight_g: int
    note: str = ""


def load_parcels(rows):
    """Build records from (key, weight_g) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = ParcelRecord(str(key), int(value))
    return list(records.values())


def total_weight_g(records):
    return sum(record.weight_g for record in records)


def top_parcels(records, n):
    """The n records with the largest weight_g; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.weight_g, record.key))[:n]


def split_parcels(records, threshold=20):
    """Return (below, at_or_above) by weight_g."""
    below = [record for record in records if record.weight_g < threshold]
    return below, [record for record in records if record.weight_g >= threshold]


def find_parcel(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_parcels(records, percent):
    """A copy of the records with weight_g changed by percent (rounded down)."""
    return [ParcelRecord(r.key, r.weight_g + r.weight_g * percent // 100, r.note) for r in records]


def merge_parcels(first, second):
    """Add the weight_g of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = ParcelRecord(old.key, old.weight_g + record.weight_g, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_parcels(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.weight_g < 0:
            problems.append(f"{record.key}: negative weight_g")
    return problems


def summarise_parcels(records):
    values = sorted(record.weight_g for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_parcel_table(records, width=18):
    lines = [f"{'key':<{width}} {'weight_g':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.weight_g:>12}")
    lines.append(f"{'total':<{width}} {total_weight_g(records):>12}")
    return "\n".join(lines) + "\n"
