# depot

A small order service for a warehouse. All money is in whole pence. All data is made up.

## Modules

| File | What it holds |
|---|---|
| `depot/models.py` | data classes |
| `depot/errors.py` | the error types |
| `depot/money.py` | parse and format money |
| `depot/catalog.py` | the products |
| `depot/inventory.py` | units per warehouse |
| `depot/validation.py` | checks on a new order |
| `depot/pricing.py` | line prices and discounts |
| `depot/tax.py` | VAT |
| `depot/shipping.py` | shipping cost |
| `depot/dates.py` | delivery dates |
| `depot/orders.py` | the order service: place, cancel, advance |
| `depot/invoice.py` | the invoice text |
| `depot/reports.py` | sales reports |
| `depot/storage.py` | orders to and from plain dicts |
| `depot/sample_data.py` | sample products, customers and stock |
| `depot/cli.py` | the command line |

## Rules

### Validation of a new order

- The customer must exist, and the order needs at least one line (`InvalidOrder`).
- Each quantity is a whole number from 1 to 999 (`InvalidOrder`). Each SKU must be in the catalog (`UnknownSku`).
- Lines with the same SKU are merged into one line (the quantities are added) before anything else
  happens. The merged quantity must also be 999 or less. Prices, discounts and stock use the merged lines.

### Pricing

- Net of a line = unit price x quantity.
- Volume discount of a line, by its quantity: 10 or more units 5 %, 50 or more 10 %, 100 or more 15 %.
- Tier discount of the customer: standard 0 %, trade 8 %, partner 12 %.
- The two percentages are added. Line discount = net x percent / 100, rounded down to a whole penny.
- Line total = net - discount. Subtotal of the order = the sum of the line totals.

### VAT

- By the customer's country: GB 20 %, IE 23 %, every other country 0 % (export).
- Products of the category `books` have 0 % in every country.
- VAT of a line = line total x percent / 100, rounded down. VAT of the order = the sum over the lines.

### Shipping

- Weight of the order = the sum of product weight x quantity over all lines, in grams.
- Zones: GB is `home`; IE, FR, DE and NL are `near`; every other country is `far`.
- Standard cost in pence:

  | Weight | home | near | far |
  |---|---|---|---|
  | up to and including 2,000 g | 395 | 895 | 1,595 |
  | up to and including 10,000 g | 695 | 1,495 | 2,995 |
  | above 10,000 g | 1,295 | 2,495 | 4,995 |

- Standard shipping in the `home` zone is free when the subtotal is 7,500 pence or more.
- Express costs the standard cost plus 50 % (rounded down). It is never free. It exists in the
  `home` zone only; express to another zone raises `InvalidOrder`.
- Total of the order = subtotal + VAT + shipping. Shipping has no VAT.

### Stock

- The warehouses have a fixed priority: `leeds`, then `pune`, then `oslo`.
- `place_order` takes the units of each line from the warehouses in that order, as many as each has.
- If the warehouses together do not have enough units for any one line, `OutOfStock` is raised and
  nothing is taken for any line.
- The order records where its units came from: `allocations` is a list of `(sku, warehouse, units)`.

### Order status

- `placed` -> `picked` -> `shipped` -> `delivered`. `advance(order_id)` moves the order one step.
- `cancel_order(order_id)` is allowed for the status `placed` or `picked` only; any other status
  raises `InvalidOrder`. It gives every unit back to the warehouse it came from and sets the status
  to `cancelled`.
- A `cancelled` or `delivered` order cannot advance (`InvalidOrder`).

### Delivery estimate

- Standard: 3 business days after the order date. Express: 1 business day.
- Business days are Monday to Friday, except the bank holidays in `dates.HOLIDAYS`.
- An order placed on a day that is not a business day counts as placed on the next business day.

### Invoice

```
Invoice ORD-0001
Customer: Asha Kulkarni (C-02)
Date: 2026-03-02

SKU      Qty  Description                   Total
TL-200     1  Folding Hand Saw             £18.95

Subtotal: £18.95
VAT: £3.79
Shipping (standard): £3.95
Total: £26.69
Delivery estimate: 2026-03-05
```

### Reports

Cancelled orders do not count in any report.

- `sales_by_category(orders, catalog)`: the sum of the line totals per category, sorted by category.
- `top_products(orders, n)`: the n SKUs with the most units; equal units are ordered by SKU.
- `daily_totals(orders)`: the sum of the order totals per order date, sorted by date.

## Tests

`run_tests.py` runs the checks and prints `OK` when all pass.