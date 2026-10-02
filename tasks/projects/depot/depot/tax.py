VAT_PERCENT = {"GB": 20, "IE": 23}   # every other country: 0 (export)
ZERO_RATED = {"books"}


def vat_percent(country, category):
    if category in ZERO_RATED:
        return 0
    return VAT_PERCENT.get(country, 0)


def vat_for_line(total_pence, country, category):
    """VAT on one line total, rounded down to a whole penny."""
    return total_pence * vat_percent(country, category) // 100