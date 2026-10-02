"""VAT, version 1 (2024): one rate on the whole subtotal. The current rule is per line (depot/tax.py)."""

VAT_V1 = {"GB": 20, "IE": 23}


def vat_v1(subtotal_pence, country):
    return subtotal_pence * VAT_V1.get(country, 0) // 100


def vat_inclusive_v1(subtotal_pence, country):
    return subtotal_pence + vat_v1(subtotal_pence, country)
