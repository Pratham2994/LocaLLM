"""Cover plan for holidays. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CoverRecord:
    key: str
    people: int
    note: str = ""


def load_covers(rows):
    """Build records from (key, people) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = CoverRecord(str(key), int(value))
    return list(records.values())


def total_people(records):
    return sum(record.people for record in records)


def top_covers(records, n):
    """The n records with the largest people; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.people, record.key))[:n]


def split_covers(records, threshold=60):
    """Return (below, at_or_above) by people."""
    below = [record for record in records if record.people < threshold]
    return below, [record for record in records if record.people >= threshold]


def find_cover(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_covers(records, percent):
    """A copy of the records with people changed by percent (rounded down)."""
    return [CoverRecord(r.key, r.people + r.people * percent // 100, r.note) for r in records]


def merge_covers(first, second):
    """Add the people of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = CoverRecord(old.key, old.people + record.people, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_covers(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.people < 0:
            problems.append(f"{record.key}: negative people")
    return problems


def summarise_covers(records):
    values = sorted(record.people for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_cover_table(records, width=18):
    lines = [f"{'key':<{width}} {'people':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.people:>12}")
    lines.append(f"{'total':<{width}} {total_people(records):>12}")
    return "\n".join(lines) + "\n"
