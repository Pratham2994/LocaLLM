"""Checks for the depot project. Prints OK when all pass."""
import json
from datetime import date

from depot import dates, money, pricing, reports, shipping, storage, tax
from depot.cli import build_service, main
from depot.errors import InvalidOrder, OutOfStock, UnknownSku
from depot.invoice import format_invoice
from depot.models import OrderLine

COUNT = 0


def check(name, got, want):
    global COUNT
    COUNT += 1
    if got != want:
        raise AssertionError(f"{name}: got {got!r}, expected {want!r}")


def raises(name, error, fn):
    global COUNT
    COUNT += 1
    try:
        fn()
    except error:
        return
    raise AssertionError(f"{name}: expected {error.__name__}")


MONDAY = date(2026, 3, 2)

# money
check("format", money.format_pence(1234567), "£12,345.67")
check("format negative", money.format_pence(-5), "-£0.05")
check("parse", [money.parse_price(t) for t in ("12.50", "7", "£1,200.5", "0.05")], [1250, 700, 120050, 5])
for bad in ("1.234", "abc", "-3"):
    raises(f"parse {bad}", ValueError, lambda bad=bad: money.parse_price(bad))

# pricing, tax, shipping
service = build_service()
catalog = service.catalog
check("volume + tier", pricing.price_line(catalog.get("TL-210"), 10, "trade"), (9400, 1222, 8178))
check("largest break", pricing.price_line(catalog.get("GD-300"), 100, "partner"), (65000, 17550, 47450))
check("vat", [tax.vat_for_line(8178, "GB", "tools"), tax.vat_for_line(8178, "IE", "tools"),
              tax.vat_for_line(8178, "GB", "books"), tax.vat_for_line(8178, "NO", "tools")], [1635, 1880, 0, 0])
check("weight bands", [shipping.standard_cost(g, "home") for g in (2000, 2001, 10000, 10001)], [395, 695, 695, 1295])
check("shipping", [shipping.shipping_cost(350, "GB", "standard", 1895), shipping.shipping_cost(350, "GB", "standard", 7500),
                   shipping.shipping_cost(350, "GB", "express", 9000), shipping.shipping_cost(350, "IE", "standard", 9000),
                   shipping.shipping_cost(350, "NO", "standard", 100)], [395, 0, 592, 895, 1595])
raises("express abroad", InvalidOrder, lambda: shipping.shipping_cost(350, "IE", "express", 100))

# dates
check("standard from Monday", dates.delivery_estimate(MONDAY, "standard"), date(2026, 3, 5))
check("standard over a weekend", dates.delivery_estimate(date(2026, 3, 6), "standard"), date(2026, 3, 11))
check("express from Saturday", dates.delivery_estimate(date(2026, 3, 7), "express"), date(2026, 3, 10))
check("standard over Easter", dates.delivery_estimate(date(2026, 4, 2), "standard"), date(2026, 4, 9))
check("express before Christmas", dates.delivery_estimate(date(2025, 12, 24), "express"), date(2025, 12, 29))

# orders
order = service.place_order("C-01", [OrderLine("TL-200", 8)], MONDAY)
check("allocations", order.allocations, [("TL-200", "leeds", 5), ("TL-200", "pune", 3)])
check("stock after order", [service.inventory.on_hand("TL-200", w) for w in ("leeds", "pune")], [0, 9])
check("order money", (order.subtotal_pence, order.vat_pence, order.shipping_pence, order.total_pence), (13948, 2789, 0, 16737))
check("storage round trip", storage.order_from_dict(json.loads(json.dumps(storage.order_to_dict(order)))), order)
service.cancel_order(order.id)
check("stock after cancel", [service.inventory.on_hand("TL-200", w) for w in ("leeds", "pune")], [5, 12])
check("status after cancel", order.status, "cancelled")
raises("cancel twice", InvalidOrder, lambda: service.cancel_order(order.id))
raises("advance a cancelled order", InvalidOrder, lambda: service.advance(order.id))

raises("all or nothing", OutOfStock,
       lambda: service.place_order("C-02", [OrderLine("BK-101", 5), OrderLine("GD-310", 4)], MONDAY))
check("nothing taken", service.inventory.on_hand("BK-101", "leeds"), 40)

merged = service.place_order("C-02", [OrderLine("TL-210", 6), OrderLine("TL-210", 6)], MONDAY)
check("merged line", [(l.sku, l.qty, l.net_pence, l.discount_pence, l.total_pence) for l in merged.lines],
      [("TL-210", 12, 11280, 564, 10716)])
check("merged allocations", merged.allocations, [("TL-210", "pune", 12)])

irish = service.place_order("C-04", [OrderLine("TL-250", 2)], MONDAY)
check("irish order", (irish.subtotal_pence, irish.vat_pence, irish.shipping_pence, irish.total_pence), (8464, 1946, 2495, 12905))
export = service.place_order("C-03", [OrderLine("BK-102", 1)], date(2026, 3, 3))
check("export order", (export.subtotal_pence, export.vat_pence, export.shipping_pence, export.total_pence), (2156, 0, 1595, 3751))

check("advance", [service.advance(irish.id).status, service.advance(irish.id).status], ["picked", "shipped"])
raises("cancel a shipped order", InvalidOrder, lambda: service.cancel_order(irish.id))
check("delivered", service.advance(irish.id).status, "delivered")
raises("advance a delivered order", InvalidOrder, lambda: service.advance(irish.id))
raises("unknown order", InvalidOrder, lambda: service.get("ORD-9999"))
raises("unknown customer", InvalidOrder, lambda: service.place_order("C-99", [OrderLine("TL-200", 1)], MONDAY))
raises("no lines", InvalidOrder, lambda: service.place_order("C-02", [], MONDAY))
raises("quantity 0", InvalidOrder, lambda: service.place_order("C-02", [OrderLine("TL-200", 0)], MONDAY))
raises("merged quantity above 999", InvalidOrder,
       lambda: service.place_order("C-02", [OrderLine("GD-300", 500), OrderLine("GD-300", 500)], MONDAY))
raises("unknown sku", UnknownSku, lambda: service.place_order("C-02", [OrderLine("XX-000", 1)], MONDAY))

# reports (the first order is cancelled)
orders = list(service.orders.values())
check("sales by category", reports.sales_by_category(orders, catalog), [("books", 2156), ("tools", 19180)])
check("top products", reports.top_products(orders, 2), [("TL-210", 12), ("TL-250", 2)])
check("daily totals", reports.daily_totals(orders), [(MONDAY, 25764), (date(2026, 3, 3), 3751)])

# catalog and inventory
check("search", [p.sku for p in catalog.search("guide")], ["BK-101"])
check("by category", [p.sku for p in catalog.by_category("tools")], ["TL-200", "TL-210", "TL-250"])
raises("unknown sku in catalog", UnknownSku, lambda: catalog.get("XX-000"))
check("low stock", build_service().inventory.low_stock(10), ["GD-310", "TL-250"])

# command line and invoice
check("stock command", main(["stock", "TL-200"]), "TL-200: leeds 5, pune 12, oslo 0 (available 17)\n")
check("low-stock command", main(["low-stock"]), "GD-310: 3\nTL-250: 9\n")
INVOICE = """Invoice ORD-0001
Customer: Asha Kulkarni (C-02)
Date: 2026-03-02

SKU      Qty  Description                   Total
TL-200     1  Folding Hand Saw             £18.95

Subtotal: £18.95
VAT: £3.79
Shipping (standard): £3.95
Total: £26.69
Delivery estimate: 2026-03-05
"""
check("quote command", main(["quote", "C-02", "TL-200:1"]), INVOICE)
fresh = build_service()
quoted = fresh.place_order("C-02", [OrderLine("TL-200", 1)], MONDAY, "express")
check("express invoice lines", format_invoice(quoted, fresh.customers["C-02"], fresh.catalog).splitlines()[-3:],
      ["Shipping (express): £5.92", "Total: £28.66", "Delivery estimate: 2026-03-03"])
print(f"OK: {COUNT} checks")
