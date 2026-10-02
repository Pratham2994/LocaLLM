from datetime import date, timedelta

HOLIDAYS = {date(2025, 12, 25), date(2025, 12, 26), date(2026, 1, 1), date(2026, 4, 3), date(2026, 4, 6)}
BUSINESS_DAYS = {"standard": 3, "express": 1}


def is_business_day(day):
    return day.weekday() < 5 and day not in HOLIDAYS


def next_business_day(day):
    """The first business day on or after `day`."""
    while not is_business_day(day):
        day += timedelta(days=1)
    return day


def add_business_days(day, n):
    """The date `n` business days after `day`. A day that is not a business day counts as the
    next business day before the counting starts."""
    day = next_business_day(day)
    while n > 0:
        day += timedelta(days=1)
        if is_business_day(day):
            n -= 1
    return day


def delivery_estimate(placed_on, method):
    return add_business_days(placed_on, BUSINESS_DAYS[method])