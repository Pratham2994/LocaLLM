"""Log of price changes. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PriceChangeRecord:
    key: str
    delta_pence: int
    note: str = ""


def load_price_changes(rows):
    """Build records from (key, delta_pence) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = PriceChangeRecord(str(key), int(value))
    return list(records.values())


def total_delta_pence(records):
    return sum(record.delta_pence for record in records)


def top_price_changes(records, n):
    """The n records with the largest delta_pence; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.delta_pence, record.key))[:n]


def split_price_changes(records, threshold=50):
    """Return (below, at_or_above) by delta_pence."""
    below = [record for record in records if record.delta_pence < threshold]
    return below, [record for record in records if record.delta_pence >= threshold]


def find_price_change(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_price_changes(records, percent):
    """A copy of the records with delta_pence changed by percent (rounded down)."""
    return [PriceChangeRecord(r.key, r.delta_pence + r.delta_pence * percent // 100, r.note) for r in records]


def merge_price_changes(first, second):
    """Add the delta_pence of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = PriceChangeRecord(old.key, old.delta_pence + record.delta_pence, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_price_changes(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.delta_pence < 0:
            problems.append(f"{record.key}: negative delta_pence")
    return problems


def summarise_price_changes(records):
    values = sorted(record.delta_pence for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_price_change_table(records, width=19):
    lines = [f"{'key':<{width}} {'delta_pence':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.delta_pence:>12}")
    lines.append(f"{'total':<{width}} {total_delta_pence(records):>12}")
    return "\n".join(lines) + "\n"
