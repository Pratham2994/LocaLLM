from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    unit_price_pence: int
    weight_g: int
    category: str


@dataclass(frozen=True)
class Customer:
    id: str
    name: str
    tier: str      # "standard", "trade" or "partner"
    country: str   # ISO code, e.g. "GB"


@dataclass(frozen=True)
class OrderLine:
    sku: str
    qty: int


@dataclass
class PricedLine:
    sku: str
    qty: int
    net_pence: int        # unit price x quantity
    discount_pence: int
    total_pence: int      # net - discount
    vat_pence: int


@dataclass
class Order:
    id: str
    customer_id: str
    placed_on: date
    method: str                               # "standard" or "express"
    lines: list[PricedLine]
    allocations: list[tuple[str, str, int]]   # (sku, warehouse, units taken there)
    subtotal_pence: int
    vat_pence: int
    shipping_pence: int
    total_pence: int
    status: str = "placed"