class DepotError(Exception):
    """Base class of all errors that depot raises on purpose."""


class UnknownSku(DepotError):
    """The SKU is not in the catalog."""


class OutOfStock(DepotError):
    """Not enough units to fill an order line."""


class InvalidOrder(DepotError):
    """The order, or the action on it, breaks a rule in README.md."""