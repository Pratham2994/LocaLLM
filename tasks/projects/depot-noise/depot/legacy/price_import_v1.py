"""Price import, version 1 (2024): semicolons, prices in pence, no header. Not the README format."""


def read_prices_v1(text):
    prices = {}
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        sku, pence = line.split(";")
        prices[sku.strip()] = int(pence)
    return prices


def apply_prices_v1(prices, table):
    """`table` is a plain dict sku -> pence. Unknown SKUs are added (the old behaviour)."""
    table.update(prices)
    return len(prices)
