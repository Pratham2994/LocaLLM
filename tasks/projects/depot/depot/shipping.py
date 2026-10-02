from depot.errors import InvalidOrder

ZONES = {"GB": "home", "IE": "near", "FR": "near", "DE": "near", "NL": "near"}   # all others: "far"
BANDS = (
    (2_000, {"home": 395, "near": 895, "far": 1_595}),      # up to and including 2 kg
    (10_000, {"home": 695, "near": 1_495, "far": 2_995}),   # up to and including 10 kg
)
HEAVY = {"home": 1_295, "near": 2_495, "far": 4_995}       # above 10 kg
FREE_FROM_PENCE = 7_500
EXPRESS_PERCENT = 50


def zone_of(country):
    return ZONES.get(country, "far")


def standard_cost(weight_g, zone):
    for limit, costs in BANDS:
        if weight_g <= limit:
            return costs[zone]
    return HEAVY[zone]


def shipping_cost(weight_g, country, method, subtotal_pence):
    """Shipping in pence for an order of this weight (README.md, "Shipping")."""
    zone = zone_of(country)
    base = standard_cost(weight_g, zone)
    if method == "express":
        if zone != "home":
            raise InvalidOrder("express is available in the home zone only")
        return base + base * EXPRESS_PERCENT // 100
    if method != "standard":
        raise InvalidOrder(f"unknown shipping method {method!r}")
    if zone == "home" and subtotal_pence >= FREE_FROM_PENCE:
        return 0
    return base