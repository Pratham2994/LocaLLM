"""Figures for the monthly review. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewRecord:
    key: str
    amount_pence: int
    note: str = ""


def load_reviews(rows):
    """Build records from (key, amount_pence) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = ReviewRecord(str(key), int(value))
    return list(records.values())


def total_amount_pence(records):
    return sum(record.amount_pence for record in records)


def top_reviews(records, n):
    """The n records with the largest amount_pence; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.amount_pence, record.key))[:n]


def split_reviews(records, threshold=20):
    """Return (below, at_or_above) by amount_pence."""
    below = [record for record in records if record.amount_pence < threshold]
    return below, [record for record in records if record.amount_pence >= threshold]


def find_review(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_reviews(records, percent):
    """A copy of the records with amount_pence changed by percent (rounded down)."""
    return [ReviewRecord(r.key, r.amount_pence + r.amount_pence * percent // 100, r.note) for r in records]


def merge_reviews(first, second):
    """Add the amount_pence of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = ReviewRecord(old.key, old.amount_pence + record.amount_pence, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_reviews(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.amount_pence < 0:
            problems.append(f"{record.key}: negative amount_pence")
    return problems


def summarise_reviews(records):
    values = sorted(record.amount_pence for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_review_table(records, width=13):
    lines = [f"{'key':<{width}} {'amount_pence':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.amount_pence:>12}")
    lines.append(f"{'total':<{width}} {total_amount_pence(records):>12}")
    return "\n".join(lines) + "\n"
