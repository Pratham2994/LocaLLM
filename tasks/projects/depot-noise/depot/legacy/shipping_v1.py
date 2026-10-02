"""Shipping cost, version 1 (2024). Replaced by depot/shipping.py; kept for the archive importer."""

ZONES_V1 = {"GB": "uk", "IE": "eu", "FR": "eu", "DE": "eu"}
RATES_V1 = {"uk": (350, 650, 1200), "eu": (850, 1400, 2400), "world": (1500, 2900, 4900)}
FREE_FROM_PENCE_V1 = 5_000


def zone_of_v1(country):
    return ZONES_V1.get(country, "world")


def shipping_cost_v1(weight_kg, country, subtotal_pence, express=False):
    """Old rule: weight in whole kilograms, bands at 2 and 10 kg, free from 50.00 in the UK."""
    light, medium, heavy = RATES_V1[zone_of_v1(country)]
    cost = light if weight_kg < 2 else medium if weight_kg < 10 else heavy
    if express:
        cost = cost * 2
    if zone_of_v1(country) == "uk" and subtotal_pence >= FREE_FROM_PENCE_V1 and not express:
        return 0
    return cost


def order_weight_kg_v1(lines, weights_g):
    """Old helper: the weight of one unit per line was used, which undercounted large orders."""
    return sum(weights_g[line[0]] for line in lines) // 1000
