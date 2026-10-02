from depot.dates import delivery_estimate
from depot.money import format_pence

NAME_WIDTH = 24


def invoice_rows(order, catalog):
    """One text row per order line: SKU, quantity, product name, line total."""
    rows = []
    for line in order.lines:
        name = catalog.get(line.sku).name[:NAME_WIDTH]
        rows.append(f"{line.sku:<8} {line.qty:>3}  {name:<{NAME_WIDTH}} {format_pence(line.total_pence):>10}")
    return rows


def format_invoice(order, customer, catalog):
    """The invoice as text. Layout: see README.md, "Invoice"."""
    out = [
        f"Invoice {order.id}",
        f"Customer: {customer.name} ({customer.id})",
        f"Date: {order.placed_on.isoformat()}",
        "",
        f"{'SKU':<8} {'Qty':>3}  {'Description':<{NAME_WIDTH}} {'Total':>10}",
    ]
    out += invoice_rows(order, catalog)
    out += [
        "",
        f"Subtotal: {format_pence(order.subtotal_pence)}",
        f"VAT: {format_pence(order.vat_pence)}",
        f"Shipping ({order.method}): {format_pence(order.shipping_pence)}",
        f"Total: {format_pence(order.total_pence)}",
        f"Delivery estimate: {delivery_estimate(order.placed_on, order.method).isoformat()}",
    ]
    return "\n".join(out) + "\n"