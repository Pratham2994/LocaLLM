"""Picking rounds per shift. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PickRoundRecord:
    key: str
    picks: int
    note: str = ""


def load_pick_rounds(rows):
    """Build records from (key, picks) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = PickRoundRecord(str(key), int(value))
    return list(records.values())


def total_picks(records):
    return sum(record.picks for record in records)


def top_pick_rounds(records, n):
    """The n records with the largest picks; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.picks, record.key))[:n]


def split_pick_rounds(records, threshold=40):
    """Return (below, at_or_above) by picks."""
    below = [record for record in records if record.picks < threshold]
    return below, [record for record in records if record.picks >= threshold]


def find_pick_round(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_pick_rounds(records, percent):
    """A copy of the records with picks changed by percent (rounded down)."""
    return [PickRoundRecord(r.key, r.picks + r.picks * percent // 100, r.note) for r in records]


def merge_pick_rounds(first, second):
    """Add the picks of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = PickRoundRecord(old.key, old.picks + record.picks, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_pick_rounds(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.picks < 0:
            problems.append(f"{record.key}: negative picks")
    return problems


def summarise_pick_rounds(records):
    values = sorted(record.picks for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_pick_round_table(records, width=16):
    lines = [f"{'key':<{width}} {'picks':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.picks:>12}")
    lines.append(f"{'total':<{width}} {total_picks(records):>12}")
    return "\n".join(lines) + "\n"
