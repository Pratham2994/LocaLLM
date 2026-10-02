"""Page plan for the printed catalog. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PageRecord:
    key: str
    items: int
    note: str = ""


def load_pages(rows):
    """Build records from (key, items) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = PageRecord(str(key), int(value))
    return list(records.values())


def total_items(records):
    return sum(record.items for record in records)


def top_pages(records, n):
    """The n records with the largest items; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.items, record.key))[:n]


def split_pages(records, threshold=70):
    """Return (below, at_or_above) by items."""
    below = [record for record in records if record.items < threshold]
    return below, [record for record in records if record.items >= threshold]


def find_page(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_pages(records, percent):
    """A copy of the records with items changed by percent (rounded down)."""
    return [PageRecord(r.key, r.items + r.items * percent // 100, r.note) for r in records]


def merge_pages(first, second):
    """Add the items of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = PageRecord(old.key, old.items + record.items, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_pages(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.items < 0:
            problems.append(f"{record.key}: negative items")
    return problems


def summarise_pages(records):
    values = sorted(record.items for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_page_table(records, width=16):
    lines = [f"{'key':<{width}} {'items':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.items:>12}")
    lines.append(f"{'total':<{width}} {total_items(records):>12}")
    return "\n".join(lines) + "\n"
