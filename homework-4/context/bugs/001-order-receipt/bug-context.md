# Bug Context: Order Receipt

## Seeded Issues

1. **Incorrect discount calculation**: the initial implementation multiplied
   the subtotal by `discount_percent` directly instead of dividing by 100.
2. **Invalid quantities accepted**: zero and negative quantities could produce
   meaningless totals.
3. **Unescaped customer input**: the customer name was interpolated directly
   into a receipt that may be displayed as HTML, enabling stored/reflected XSS
   in an HTML consumer.

## Before State

The seeded implementation was equivalent to:

```python
subtotal = unit_price * quantity
total = subtotal - (subtotal * discount_percent)
return f"Customer: {customer_name}\nTotal: ${total}"
```

It had no quantity, price, discount, or blank-name validation. Reproduction
inputs were:

- price `19.99`, quantity `2`, discount `10` returned a negative total instead
  of `$35.98`;
- quantity `-1` was accepted;
- customer `<script>alert("x")</script>` was returned unchanged.

## Expected State

- Percentage discounts divide by 100 and money rounds half-up to two decimals.
- Price and quantity must be positive; discounts must be from 0 through 100.
- Customer-controlled text is stripped, required, and HTML-escaped.
- Regression tests cover all three seeded issues.

Current fixed implementation: `homework-4/src/order_receipt/order.py:11`.
Regression tests: `homework-4/tests/test_order.py:17`.
