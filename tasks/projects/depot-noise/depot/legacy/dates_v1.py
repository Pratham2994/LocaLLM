"""Delivery dates, version 1 (2024): weekends only, no bank holidays. See depot/dates.py for the current rule."""
from datetime import timedelta


def is_working_day_v1(day):
    return day.weekday() < 5


def add_working_days_v1(day, n):
    while n > 0:
        day += timedelta(days=1)
        if is_working_day_v1(day):
            n -= 1
    return day


def delivery_estimate_v1(placed_on, express=False):
    return add_working_days_v1(placed_on, 1 if express else 4)
