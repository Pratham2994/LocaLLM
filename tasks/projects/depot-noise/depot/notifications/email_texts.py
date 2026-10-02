"""Email text blocks. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EmailBlockRecord:
    key: str
    length: int
    note: str = ""


def load_email_blocks(rows):
    """Build records from (key, length) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = EmailBlockRecord(str(key), int(value))
    return list(records.values())


def total_length(records):
    return sum(record.length for record in records)


def top_email_blocks(records, n):
    """The n records with the largest length; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.length, record.key))[:n]


def split_email_blocks(records, threshold=10):
    """Return (below, at_or_above) by length."""
    below = [record for record in records if record.length < threshold]
    return below, [record for record in records if record.length >= threshold]


def find_email_block(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_email_blocks(records, percent):
    """A copy of the records with length changed by percent (rounded down)."""
    return [EmailBlockRecord(r.key, r.length + r.length * percent // 100, r.note) for r in records]


def merge_email_blocks(first, second):
    """Add the length of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = EmailBlockRecord(old.key, old.length + record.length, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_email_blocks(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.length < 0:
            problems.append(f"{record.key}: negative length")
    return problems


def summarise_email_blocks(records):
    values = sorted(record.length for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_email_block_table(records, width=15):
    lines = [f"{'key':<{width}} {'length':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.length:>12}")
    lines.append(f"{'total':<{width}} {total_length(records):>12}")
    return "\n".join(lines) + "\n"
