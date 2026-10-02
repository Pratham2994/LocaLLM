from depot.dates import delivery_estimate
from depot.errors import InvalidOrder
from depot.models import Order, PricedLine
from depot.pricing import price_line
from depot.shipping import shipping_cost
from depot.tax import vat_for_line
from depot.validation import validate_order

STATUS_FLOW = ("placed", "picked", "shipped", "delivered")
CANCELLABLE = ("placed", "picked")


class OrderService:
    """Places, cancels and moves orders. Rules: README.md."""

    def __init__(self, catalog, inventory, customers):
        self.catalog = catalog
        self.inventory = inventory
        self.customers = {customer.id: customer for customer in customers}
        self.orders = {}
        self._next_number = 1

    def place_order(self, customer_id, lines, placed_on, method="standard"):
        lines = validate_order(customer_id, lines, self.customers, self.catalog)
        customer = self.customers[customer_id]
        # Plan the picking first: OutOfStock must be raised before any unit is taken.
        plans = [(line.sku, self.inventory.plan(line.sku, line.qty)) for line in lines]

        priced, weight_g = [], 0
        for line in lines:
            product = self.catalog.get(line.sku)
            net, discount, total = price_line(product, line.qty, customer.tier)
            vat = vat_for_line(total, customer.country, product.category)
            priced.append(PricedLine(line.sku, line.qty, net, discount, total, vat))
            weight_g += product.weight_g * line.qty
        subtotal = sum(line.total_pence for line in priced)
        vat_total = sum(line.vat_pence for line in priced)
        shipping = shipping_cost(weight_g, customer.country, method, subtotal)

        allocations = []
        for sku, plan in plans:
            for warehouse, units in plan:
                self.inventory.take(sku, warehouse, units)
                allocations.append((sku, warehouse, units))

        order = Order(
            id=f"ORD-{self._next_number:04d}", customer_id=customer_id, placed_on=placed_on,
            method=method, lines=priced, allocations=allocations, subtotal_pence=subtotal,
            vat_pence=vat_total, shipping_pence=shipping,
            total_pence=subtotal + vat_total + shipping,
        )
        self._next_number += 1
        self.orders[order.id] = order
        return order

    def get(self, order_id):
        try:
            return self.orders[order_id]
        except KeyError:
            raise InvalidOrder(f"unknown order {order_id}") from None

    def cancel_order(self, order_id):
        order = self.get(order_id)
        if order.status not in CANCELLABLE:
            raise InvalidOrder(f"an order with status {order.status} cannot be cancelled")
        for sku, warehouse, units in order.allocations:
            self.inventory.receive(sku, warehouse, units)
        order.status = "cancelled"
        return order

    def advance(self, order_id):
        """Move the order one step along placed -> picked -> shipped -> delivered."""
        order = self.get(order_id)
        if order.status not in STATUS_FLOW[:-1]:
            raise InvalidOrder(f"an order with status {order.status} cannot advance")
        order.status = STATUS_FLOW[STATUS_FLOW.index(order.status) + 1]
        return order

    def estimate(self, order_id):
        order = self.get(order_id)
        return delivery_estimate(order.placed_on, order.method)