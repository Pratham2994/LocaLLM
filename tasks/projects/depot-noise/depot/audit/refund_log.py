"""Log of refunds paid. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RefundRecord:
    key: str
    refund_pence: int
    note: str = ""


def load_refunds(rows):
    """Build records from (key, refund_pence) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = RefundRecord(str(key), int(value))
    return list(records.values())


def total_refund_pence(records):
    return sum(record.refund_pence for record in records)


def top_refunds(records, n):
    """The n records with the largest refund_pence; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.refund_pence, record.key))[:n]


def split_refunds(records, threshold=20):
    """Return (below, at_or_above) by refund_pence."""
    below = [record for record in records if record.refund_pence < threshold]
    return below, [record for record in records if record.refund_pence >= threshold]


def find_refund(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_refunds(records, percent):
    """A copy of the records with refund_pence changed by percent (rounded down)."""
    return [RefundRecord(r.key, r.refund_pence + r.refund_pence * percent // 100, r.note) for r in records]


def merge_refunds(first, second):
    """Add the refund_pence of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = RefundRecord(old.key, old.refund_pence + record.refund_pence, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_refunds(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.refund_pence < 0:
            problems.append(f"{record.key}: negative refund_pence")
    return problems


def summarise_refunds(records):
    values = sorted(record.refund_pence for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_refund_table(records, width=14):
    lines = [f"{'key':<{width}} {'refund_pence':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.refund_pence:>12}")
    lines.append(f"{'total':<{width}} {total_refund_pence(records):>12}")
    return "\n".join(lines) + "\n"
