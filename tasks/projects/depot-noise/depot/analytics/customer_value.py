"""Lifetime value per customer. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CustomerValueRecord:
    key: str
    value_pence: int
    note: str = ""


def load_customer_values(rows):
    """Build records from (key, value_pence) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = CustomerValueRecord(str(key), int(value))
    return list(records.values())


def total_value_pence(records):
    return sum(record.value_pence for record in records)


def top_customer_values(records, n):
    """The n records with the largest value_pence; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.value_pence, record.key))[:n]


def split_customer_values(records, threshold=30):
    """Return (below, at_or_above) by value_pence."""
    below = [record for record in records if record.value_pence < threshold]
    return below, [record for record in records if record.value_pence >= threshold]


def find_customer_value(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_customer_values(records, percent):
    """A copy of the records with value_pence changed by percent (rounded down)."""
    return [CustomerValueRecord(r.key, r.value_pence + r.value_pence * percent // 100, r.note) for r in records]


def merge_customer_values(first, second):
    """Add the value_pence of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = CustomerValueRecord(old.key, old.value_pence + record.value_pence, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_customer_values(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.value_pence < 0:
            problems.append(f"{record.key}: negative value_pence")
    return problems


def summarise_customer_values(records):
    values = sorted(record.value_pence for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_customer_value_table(records, width=14):
    lines = [f"{'key':<{width}} {'value_pence':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.value_pence:>12}")
    lines.append(f"{'total':<{width}} {total_value_pence(records):>12}")
    return "\n".join(lines) + "\n"
