from depot.errors import UnknownSku


class Catalog:
    """The products that can be ordered, by SKU."""

    def __init__(self, products=()):
        self._by_sku = {}
        for product in products:
            self.add(product)

    def add(self, product):
        if product.sku in self._by_sku:
            raise ValueError(f"duplicate sku {product.sku}")
        self._by_sku[product.sku] = product

    def get(self, sku):
        try:
            return self._by_sku[sku]
        except KeyError:
            raise UnknownSku(sku) from None

    def __contains__(self, sku):
        return sku in self._by_sku

    def search(self, text):
        """Products whose name contains the text (any letter case), sorted by SKU."""
        needle = text.casefold()
        return sorted((p for p in self._by_sku.values() if needle in p.name.casefold()), key=lambda p: p.sku)

    def by_category(self, category):
        return sorted((p for p in self._by_sku.values() if p.category == category), key=lambda p: p.sku)