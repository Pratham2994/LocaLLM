import argparse
from datetime import date

from depot.inventory import WAREHOUSES
from depot.invoice import format_invoice
from depot.models import OrderLine
from depot.orders import OrderService
from depot.sample_data import CUSTOMERS, sample_catalog, sample_inventory


def build_service():
    """A fresh service on the sample data."""
    return OrderService(sample_catalog(), sample_inventory(), CUSTOMERS)


def parse_line(text):
    """'TL-200:3' -> OrderLine('TL-200', 3)."""
    sku, _, qty = text.partition(":")
    if not sku or not qty.isdigit():
        raise argparse.ArgumentTypeError(f"expected SKU:QTY, got {text!r}")
    return OrderLine(sku, int(qty))


def build_parser():
    parser = argparse.ArgumentParser(prog="depot")
    commands = parser.add_subparsers(dest="command", required=True)

    stock = commands.add_parser("stock", help="units of one SKU per warehouse")
    stock.add_argument("sku")

    low = commands.add_parser("low-stock", help="SKUs with few units left")
    low.add_argument("--threshold", type=int, default=10)

    quote = commands.add_parser("quote", help="price an order and print its invoice")
    quote.add_argument("customer")
    quote.add_argument("lines", nargs="+", type=parse_line, metavar="SKU:QTY")
    quote.add_argument("--express", action="store_true")
    quote.add_argument("--date", type=date.fromisoformat, default=date(2026, 3, 2))
    return parser


def main(argv=None, service=None):
    """Run one command and return its output as text."""
    args = build_parser().parse_args(argv)
    service = service or build_service()
    if args.command == "stock":
        service.catalog.get(args.sku)
        per_warehouse = ", ".join(f"{w} {service.inventory.on_hand(args.sku, w)}" for w in WAREHOUSES)
        return f"{args.sku}: {per_warehouse} (available {service.inventory.available(args.sku)})\n"
    if args.command == "low-stock":
        skus = service.inventory.low_stock(args.threshold)
        return "".join(f"{sku}: {service.inventory.available(sku)}\n" for sku in skus)
    order = service.place_order(args.customer, args.lines, args.date,
                                "express" if args.express else "standard")
    return format_invoice(order, service.customers[args.customer], service.catalog)