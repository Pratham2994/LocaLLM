from depot.errors import OutOfStock

WAREHOUSES = ("leeds", "pune", "oslo")   # the priority order for picking


class Inventory:
    """Units on hand per SKU and warehouse."""

    def __init__(self):
        self._stock = {}   # (sku, warehouse) -> units

    def receive(self, sku, warehouse, qty):
        if warehouse not in WAREHOUSES:
            raise ValueError(f"unknown warehouse {warehouse!r}")
        if qty <= 0:
            raise ValueError("qty must be positive")
        self._stock[(sku, warehouse)] = self.on_hand(sku, warehouse) + qty

    def on_hand(self, sku, warehouse):
        return self._stock.get((sku, warehouse), 0)

    def available(self, sku):
        return sum(self.on_hand(sku, warehouse) for warehouse in WAREHOUSES)

    def plan(self, sku, qty):
        """Which warehouses would supply `qty` units: a list of (warehouse, units) in priority
        order. Takes nothing. Raises OutOfStock if all warehouses together have too few."""
        if qty > self.available(sku):
            raise OutOfStock(f"{sku}: wanted {qty}, available {self.available(sku)}")
        plan, left = [], qty
        for warehouse in WAREHOUSES:
            units = min(left, self.on_hand(sku, warehouse))
            if units:
                plan.append((warehouse, units))
                left -= units
            if left == 0:
                break
        return plan

    def take(self, sku, warehouse, qty):
        if qty > self.on_hand(sku, warehouse):
            raise OutOfStock(f"{sku}: {warehouse} has only {self.on_hand(sku, warehouse)}")
        self._stock[(sku, warehouse)] -= qty

    def low_stock(self, threshold):
        """SKUs with fewer than `threshold` units available in total, sorted."""
        skus = {sku for sku, _ in self._stock}
        return sorted(sku for sku in skus if self.available(sku) < threshold)