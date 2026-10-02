from depot.catalog import Catalog
from depot.inventory import Inventory
from depot.models import Customer, Product

PRODUCTS = [
    Product("BK-101", "Field Guide to Moss", 1_299, 420, "books"),
    Product("BK-102", "Atlas of Small Rivers", 2_450, 1_100, "books"),
    Product("TL-200", "Folding Hand Saw", 1_895, 350, "tools"),
    Product("TL-210", "Brass Plumb Bob", 940, 280, "tools"),
    Product("TL-250", "Bench Vice 100 mm", 4_600, 5_200, "tools"),
    Product("GD-300", "Seed Tray (pack of 5)", 650, 300, "garden"),
    Product("GD-310", "Copper Watering Can", 3_895, 900, "garden"),
    Product("EL-400", "Solar Path Light", 1_150, 240, "electrical"),
]

CUSTOMERS = [
    Customer("C-01", "Northwind Traders", "trade", "GB"),
    Customer("C-02", "Asha Kulkarni", "standard", "GB"),
    Customer("C-03", "Fjord Supplies AS", "partner", "NO"),
    Customer("C-04", "Dubhlinn Hardware", "trade", "IE"),
]

# sku: (leeds, pune, oslo)
STOCK = {
    "BK-101": (40, 0, 10),
    "BK-102": (6, 20, 0),
    "TL-200": (5, 12, 0),
    "TL-210": (0, 30, 30),
    "TL-250": (3, 3, 3),
    "GD-300": (200, 400, 0),
    "GD-310": (2, 0, 1),
    "EL-400": (15, 15, 15),
}


def sample_catalog():
    return Catalog(PRODUCTS)


def sample_inventory():
    inventory = Inventory()
    for sku, (leeds, pune, oslo) in STOCK.items():
        for warehouse, units in (("leeds", leeds), ("pune", pune), ("oslo", oslo)):
            if units:
                inventory.receive(sku, warehouse, units)
    return inventory