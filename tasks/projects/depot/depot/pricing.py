VOLUME_BREAKS = ((100, 15), (50, 10), (10, 5))   # (minimum units, percent), largest first
TIER_PERCENT = {"standard": 0, "trade": 8, "partner": 12}


def volume_percent(qty):
    for minimum, percent in VOLUME_BREAKS:
        if qty >= minimum:
            return percent
    return 0


def price_line(product, qty, tier):
    """Return (net, discount, total) in pence for one order line (README.md, "Pricing")."""
    net = product.unit_price_pence * qty
    percent = volume_percent(qty) + TIER_PERCENT[tier]
    discount = net * percent // 100
    return net, discount, net - discount