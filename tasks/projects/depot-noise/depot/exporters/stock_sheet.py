"""Stock sheet for the weekly count. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SheetRowRecord:
    key: str
    counted: int
    note: str = ""


def load_sheet_rows(rows):
    """Build records from (key, counted) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = SheetRowRecord(str(key), int(value))
    return list(records.values())


def total_counted(records):
    return sum(record.counted for record in records)


def top_sheet_rows(records, n):
    """The n records with the largest counted; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.counted, record.key))[:n]


def split_sheet_rows(records, threshold=50):
    """Return (below, at_or_above) by counted."""
    below = [record for record in records if record.counted < threshold]
    return below, [record for record in records if record.counted >= threshold]


def find_sheet_row(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_sheet_rows(records, percent):
    """A copy of the records with counted changed by percent (rounded down)."""
    return [SheetRowRecord(r.key, r.counted + r.counted * percent // 100, r.note) for r in records]


def merge_sheet_rows(first, second):
    """Add the counted of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = SheetRowRecord(old.key, old.counted + record.counted, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_sheet_rows(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.counted < 0:
            problems.append(f"{record.key}: negative counted")
    return problems


def summarise_sheet_rows(records):
    values = sorted(record.counted for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_sheet_row_table(records, width=14):
    lines = [f"{'key':<{width}} {'counted':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.counted:>12}")
    lines.append(f"{'total':<{width}} {total_counted(records):>12}")
    return "\n".join(lines) + "\n"
