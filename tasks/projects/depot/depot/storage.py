from datetime import date

from depot.models import Order, PricedLine


def order_to_dict(order):
    """A plain dict that json.dumps accepts."""
    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "placed_on": order.placed_on.isoformat(),
        "method": order.method,
        "status": order.status,
        "lines": [vars(line).copy() for line in order.lines],
        "allocations": [list(item) for item in order.allocations],
        "subtotal_pence": order.subtotal_pence,
        "vat_pence": order.vat_pence,
        "shipping_pence": order.shipping_pence,
        "total_pence": order.total_pence,
    }


def order_from_dict(data):
    return Order(
        id=data["id"],
        customer_id=data["customer_id"],
        placed_on=date.fromisoformat(data["placed_on"]),
        method=data["method"],
        lines=[PricedLine(**line) for line in data["lines"]],
        allocations=[tuple(item) for item in data["allocations"]],
        subtotal_pence=data["subtotal_pence"],
        vat_pence=data["vat_pence"],
        shipping_pence=data["shipping_pence"],
        total_pence=data["total_pence"],
        status=data["status"],
    )