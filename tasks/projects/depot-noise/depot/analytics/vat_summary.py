"""VAT collected per country. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VatTotalRecord:
    key: str
    vat_pence: int
    note: str = ""


def load_vat_totals(rows):
    """Build records from (key, vat_pence) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = VatTotalRecord(str(key), int(value))
    return list(records.values())


def total_vat_pence(records):
    return sum(record.vat_pence for record in records)


def top_vat_totals(records, n):
    """The n records with the largest vat_pence; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.vat_pence, record.key))[:n]


def split_vat_totals(records, threshold=70):
    """Return (below, at_or_above) by vat_pence."""
    below = [record for record in records if record.vat_pence < threshold]
    return below, [record for record in records if record.vat_pence >= threshold]


def find_vat_total(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_vat_totals(records, percent):
    """A copy of the records with vat_pence changed by percent (rounded down)."""
    return [VatTotalRecord(r.key, r.vat_pence + r.vat_pence * percent // 100, r.note) for r in records]


def merge_vat_totals(first, second):
    """Add the vat_pence of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = VatTotalRecord(old.key, old.vat_pence + record.vat_pence, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_vat_totals(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.vat_pence < 0:
            problems.append(f"{record.key}: negative vat_pence")
    return problems


def summarise_vat_totals(records):
    values = sorted(record.vat_pence for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_vat_total_table(records, width=18):
    lines = [f"{'key':<{width}} {'vat_pence':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.vat_pence:>12}")
    lines.append(f"{'total':<{width}} {total_vat_pence(records):>12}")
    return "\n".join(lines) + "\n"
