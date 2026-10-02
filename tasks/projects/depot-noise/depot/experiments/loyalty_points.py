"""Draft: loyalty points. Not wired in."""

POINTS_PER_POUND = 2


def points_for(total_pence, tier="standard"):
    bonus = {"standard": 0, "trade": 10, "partner": 25}.get(tier, 0)
    base = total_pence // 100 * POINTS_PER_POUND
    return base + base * bonus // 100


def redeem(points, rate_pence=1):
    return points * rate_pence
