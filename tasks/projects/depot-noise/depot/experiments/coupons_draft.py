"""Draft from a 2025 workshop. Not wired in. If coupons are built, README.md gives the rules."""

DRAFT_COUPONS = {"WELCOME15": 15, "BULK20": 20}
DRAFT_CAP = 40


def draft_discount(net_pence, percent, coupon=None):
    """Idea: the coupon replaces the other discounts when it is larger."""
    extra = DRAFT_COUPONS.get(coupon, 0)
    return net_pence * min(max(percent, extra), DRAFT_CAP) // 100
