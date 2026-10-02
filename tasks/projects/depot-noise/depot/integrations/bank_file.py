"""Reader for the bank's payment file. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentRecord:
    key: str
    amount_pence: int
    note: str = ""


def load_payments(rows):
    """Build records from (key, amount_pence) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = PaymentRecord(str(key), int(value))
    return list(records.values())


def total_amount_pence(records):
    return sum(record.amount_pence for record in records)


def top_payments(records, n):
    """The n records with the largest amount_pence; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.amount_pence, record.key))[:n]


def split_payments(records, threshold=40):
    """Return (below, at_or_above) by amount_pence."""
    below = [record for record in records if record.amount_pence < threshold]
    return below, [record for record in records if record.amount_pence >= threshold]


def find_payment(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_payments(records, percent):
    """A copy of the records with amount_pence changed by percent (rounded down)."""
    return [PaymentRecord(r.key, r.amount_pence + r.amount_pence * percent // 100, r.note) for r in records]


def merge_payments(first, second):
    """Add the amount_pence of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = PaymentRecord(old.key, old.amount_pence + record.amount_pence, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_payments(records):
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


def summarise_payments(records):
    values = sorted(record.amount_pence for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_payment_table(records, width=20):
    lines = [f"{'key':<{width}} {'amount_pence':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.amount_pence:>12}")
    lines.append(f"{'total':<{width}} {total_amount_pence(records):>12}")
    return "\n".join(lines) + "\n"
