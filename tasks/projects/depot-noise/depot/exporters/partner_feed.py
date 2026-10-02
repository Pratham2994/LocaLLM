"""Product feed for partner shops. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class FeedItemRecord:
    key: str
    price_pence: int
    note: str = ""


def load_feed_items(rows):
    """Build records from (key, price_pence) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = FeedItemRecord(str(key), int(value))
    return list(records.values())


def total_price_pence(records):
    return sum(record.price_pence for record in records)


def top_feed_items(records, n):
    """The n records with the largest price_pence; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.price_pence, record.key))[:n]


def split_feed_items(records, threshold=30):
    """Return (below, at_or_above) by price_pence."""
    below = [record for record in records if record.price_pence < threshold]
    return below, [record for record in records if record.price_pence >= threshold]


def find_feed_item(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_feed_items(records, percent):
    """A copy of the records with price_pence changed by percent (rounded down)."""
    return [FeedItemRecord(r.key, r.price_pence + r.price_pence * percent // 100, r.note) for r in records]


def merge_feed_items(first, second):
    """Add the price_pence of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = FeedItemRecord(old.key, old.price_pence + record.price_pence, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_feed_items(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.price_pence < 0:
            problems.append(f"{record.key}: negative price_pence")
    return problems


def summarise_feed_items(records):
    values = sorted(record.price_pence for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_feed_item_table(records, width=12):
    lines = [f"{'key':<{width}} {'price_pence':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.price_pence:>12}")
    lines.append(f"{'total':<{width}} {total_price_pence(records):>12}")
    return "\n".join(lines) + "\n"
