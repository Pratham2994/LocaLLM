import re

_PRICE = re.compile(r"\d+(\.\d{1,2})?")


def format_pence(pence):
    """1234567 -> '£12,345.67'; -5 -> '-£0.05'."""
    sign = "-" if pence < 0 else ""
    pounds, rest = divmod(abs(pence), 100)
    return f"{sign}£{pounds:,}.{rest:02d}"


def parse_price(text):
    """'12.50' -> 1250, '7' -> 700, '£1,200.5' -> 120050. Raises ValueError for anything else."""
    cleaned = text.strip().lstrip("£").replace(",", "")
    if not _PRICE.fullmatch(cleaned):
        raise ValueError(f"not a price: {text!r}")
    whole, _, fraction = cleaned.partition(".")
    return int(whole) * 100 + int(fraction.ljust(2, "0")) if fraction else int(whole) * 100