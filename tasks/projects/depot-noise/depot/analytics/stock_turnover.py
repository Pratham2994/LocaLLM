"""Units sold against units held. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TurnoverRecord:
    key: str
    units_sold: int
    note: str = ""


def load_turnovers(rows):
    """Build records from (key, units_sold) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = TurnoverRecord(str(key), int(value))
    return list(records.values())


def total_units_sold(records):
    return sum(record.units_sold for record in records)


def top_turnovers(records, n):
    """The n records with the largest units_sold; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.units_sold, record.key))[:n]


def split_turnovers(records, threshold=10):
    """Return (below, at_or_above) by units_sold."""
    below = [record for record in records if record.units_sold < threshold]
    return below, [record for record in records if record.units_sold >= threshold]


def find_turnover(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_turnovers(records, percent):
    """A copy of the records with units_sold changed by percent (rounded down)."""
    return [TurnoverRecord(r.key, r.units_sold + r.units_sold * percent // 100, r.note) for r in records]


def merge_turnovers(first, second):
    """Add the units_sold of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = TurnoverRecord(old.key, old.units_sold + record.units_sold, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_turnovers(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.units_sold < 0:
            problems.append(f"{record.key}: negative units_sold")
    return problems


def summarise_turnovers(records):
    values = sorted(record.units_sold for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_turnover_table(records, width=19):
    lines = [f"{'key':<{width}} {'units_sold':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.units_sold:>12}")
    lines.append(f"{'total':<{width}} {total_units_sold(records):>12}")
    return "\n".join(lines) + "\n"
