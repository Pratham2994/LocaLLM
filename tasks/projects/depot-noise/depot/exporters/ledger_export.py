"""Rows for the accounts ledger. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class LedgerRowRecord:
    key: str
    amount_pence: int
    note: str = ""


def load_ledger_rows(rows):
    """Build records from (key, amount_pence) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = LedgerRowRecord(str(key), int(value))
    return list(records.values())


def total_amount_pence(records):
    return sum(record.amount_pence for record in records)


def top_ledger_rows(records, n):
    """The n records with the largest amount_pence; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.amount_pence, record.key))[:n]


def split_ledger_rows(records, threshold=40):
    """Return (below, at_or_above) by amount_pence."""
    below = [record for record in records if record.amount_pence < threshold]
    return below, [record for record in records if record.amount_pence >= threshold]


def find_ledger_row(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_ledger_rows(records, percent):
    """A copy of the records with amount_pence changed by percent (rounded down)."""
    return [LedgerRowRecord(r.key, r.amount_pence + r.amount_pence * percent // 100, r.note) for r in records]


def merge_ledger_rows(first, second):
    """Add the amount_pence of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = LedgerRowRecord(old.key, old.amount_pence + record.amount_pence, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_ledger_rows(records):
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


def summarise_ledger_rows(records):
    values = sorted(record.amount_pence for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_ledger_row_table(records, width=13):
    lines = [f"{'key':<{width}} {'amount_pence':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.amount_pence:>12}")
    lines.append(f"{'total':<{width}} {total_amount_pence(records):>12}")
    return "\n".join(lines) + "\n"
