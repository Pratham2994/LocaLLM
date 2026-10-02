def _live(orders):
    """Cancelled orders do not count in any report."""
    return [order for order in orders if order.status != "cancelled"]


def sales_by_category(orders, catalog):
    """[(category, pence)]: the sum of the line totals per product category, sorted by category."""
    totals = {}
    for order in _live(orders):
        for line in order.lines:
            category = catalog.get(line.sku).category
            totals[category] = totals.get(category, 0) + line.total_pence
    return sorted(totals.items())


def top_products(orders, n):
    """[(sku, units)]: the n SKUs with the most units sold. Equal units: lower SKU first."""
    units = {}
    for order in _live(orders):
        for line in order.lines:
            units[line.sku] = units.get(line.sku, 0) + line.qty
    return sorted(units.items(), key=lambda item: (-item[1], item[0]))[:n]


def daily_totals(orders):
    """[(date, pence)]: the sum of the order totals per order date, sorted by date."""
    totals = {}
    for order in _live(orders):
        totals[order.placed_on] = totals.get(order.placed_on, 0) + order.total_pence
    return sorted(totals.items())