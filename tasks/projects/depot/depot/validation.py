from depot.errors import InvalidOrder
from depot.models import OrderLine

MAX_QTY = 999


def merge_lines(lines):
    """Lines with the same SKU become one line (quantities added). First-seen order is kept."""
    totals = {}
    for line in lines:
        totals[line.sku] = totals.get(line.sku, 0) + line.qty
    return [OrderLine(sku, qty) for sku, qty in totals.items()]


def validate_order(customer_id, lines, customers, catalog):
    """Check a new order (README.md, "Validation") and return its merged lines."""
    if customer_id not in customers:
        raise InvalidOrder(f"unknown customer {customer_id}")
    if not lines:
        raise InvalidOrder("an order needs at least one line")
    for line in lines:
        if not isinstance(line.qty, int) or isinstance(line.qty, bool) or not 1 <= line.qty <= MAX_QTY:
            raise InvalidOrder(f"{line.sku}: quantity must be a whole number from 1 to {MAX_QTY}")
        catalog.get(line.sku)   # raises UnknownSku
    merged = merge_lines(lines)
    for line in merged:
        if line.qty > MAX_QTY:
            raise InvalidOrder(f"{line.sku}: {line.qty} units in total, the maximum is {MAX_QTY}")
    return merged