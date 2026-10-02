"""Notes from a 2025 workshop about returns. Ideas only; README.md is the source of truth.

- idea: returned units go back to the warehouse they were picked from
- idea: shipping is refunded when the whole order comes back
- idea: a return is allowed for a shipped order too
"""


def draft_refund(line_total_pence, vat_pence, returned, ordered):
    """Idea: round the refund to the nearest penny (README.md may say something else)."""
    return round((line_total_pence + vat_pence) * returned / ordered)
