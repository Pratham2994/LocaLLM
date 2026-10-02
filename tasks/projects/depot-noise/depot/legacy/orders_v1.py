"""Order flow, version 1 (2024). Replaced by depot/orders.py; kept for the archive importer."""
from depot.legacy.shipping_v1 import order_weight_kg_v1, shipping_cost_v1
from depot.legacy.vat_v1 import vat_v1


def place_order_v1(customer, lines, prices, weights_g, stock):
    """lines: list of (sku, qty). Takes the stock first, then prices the order (the old behaviour)."""
    for sku, qty in lines:
        if stock.get(sku, 0) < qty:
            raise ValueError(f"out of stock: {sku}")
    for sku, qty in lines:
        stock[sku] -= qty
    subtotal = sum(prices[sku] * qty for sku, qty in lines)
    shipping = shipping_cost_v1(order_weight_kg_v1(lines, weights_g), customer["country"], subtotal)
    vat = vat_v1(subtotal, customer["country"])
    return {"customer": customer["id"], "lines": list(lines), "subtotal": subtotal, "vat": vat,
            "shipping": shipping, "total": subtotal + vat + shipping, "status": "new"}


def cancel_order_v1(order, stock):
    """Old rule: every unit goes back to the main stock, whatever the order's status is."""
    for sku, qty in order["lines"]:
        stock[sku] = stock.get(sku, 0) + qty
    order["status"] = "cancelled"
    return order
