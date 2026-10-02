"""What customers paid for shipping. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ShippingSpendRecord:
    key: str
    pence: int
    note: str = ""


def load_shipping_spends(rows):
    """Build records from (key, pence) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = ShippingSpendRecord(str(key), int(value))
    return list(records.values())


def total_pence(records):
    return sum(record.pence for record in records)


def top_shipping_spends(records, n):
    """The n records with the largest pence; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.pence, record.key))[:n]


def split_shipping_spends(records, threshold=60):
    """Return (below, at_or_above) by pence."""
    below = [record for record in records if record.pence < threshold]
    return below, [record for record in records if record.pence >= threshold]


def find_shipping_spend(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_shipping_spends(records, percent):
    """A copy of the records with pence changed by percent (rounded down)."""
    return [ShippingSpendRecord(r.key, r.pence + r.pence * percent // 100, r.note) for r in records]


def merge_shipping_spends(first, second):
    """Add the pence of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = ShippingSpendRecord(old.key, old.pence + record.pence, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_shipping_spends(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.pence < 0:
            problems.append(f"{record.key}: negative pence")
    return problems


def summarise_shipping_spends(records):
    values = sorted(record.pence for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_shipping_spend_table(records, width=17):
    lines = [f"{'key':<{width}} {'pence':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.pence:>12}")
    lines.append(f"{'total':<{width}} {total_pence(records):>12}")
    return "\n".join(lines) + "\n"
