"""Address labels per courier batch. Not used by the order service (docs/STRUCTURE.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class LabelBatchRecord:
    key: str
    labels: int
    note: str = ""


def load_label_batches(rows):
    """Build records from (key, labels) pairs. A later pair with the same key replaces the earlier one."""
    records = {}
    for key, value in rows:
        records[key] = LabelBatchRecord(str(key), int(value))
    return list(records.values())


def total_labels(records):
    return sum(record.labels for record in records)


def top_label_batches(records, n):
    """The n records with the largest labels; equal values are ordered by key."""
    return sorted(records, key=lambda record: (-record.labels, record.key))[:n]


def split_label_batches(records, threshold=60):
    """Return (below, at_or_above) by labels."""
    below = [record for record in records if record.labels < threshold]
    return below, [record for record in records if record.labels >= threshold]


def find_label_batch(records, key):
    for record in records:
        if record.key == key:
            return record
    raise KeyError(key)


def scale_label_batches(records, percent):
    """A copy of the records with labels changed by percent (rounded down)."""
    return [LabelBatchRecord(r.key, r.labels + r.labels * percent // 100, r.note) for r in records]


def merge_label_batches(first, second):
    """Add the labels of records with the same key; keep the order of first appearance."""
    merged = {}
    for record in list(first) + list(second):
        if record.key in merged:
            old = merged[record.key]
            merged[record.key] = LabelBatchRecord(old.key, old.labels + record.labels, old.note or record.note)
        else:
            merged[record.key] = record
    return list(merged.values())


def validate_label_batches(records):
    """Return a list of problems as text; an empty list means the records are fine."""
    problems = []
    seen = set()
    for record in records:
        if record.key in seen:
            problems.append(f"duplicate key {record.key}")
        seen.add(record.key)
        if record.labels < 0:
            problems.append(f"{record.key}: negative labels")
    return problems


def summarise_label_batches(records):
    values = sorted(record.labels for record in records)
    if not values:
        return {"count": 0, "total": 0, "smallest": None, "largest": None, "median": None}
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) // 2
    return {"count": len(values), "total": sum(values), "smallest": values[0], "largest": values[-1], "median": median}


def format_label_batch_table(records, width=15):
    lines = [f"{'key':<{width}} {'labels':>12}"]
    for record in records:
        lines.append(f"{record.key:<{width}} {record.labels:>12}")
    lines.append(f"{'total':<{width}} {total_labels(records):>12}")
    return "\n".join(lines) + "\n"
