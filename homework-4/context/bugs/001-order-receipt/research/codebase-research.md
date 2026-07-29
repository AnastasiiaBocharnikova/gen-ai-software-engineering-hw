# Codebase Research: Order Receipt

## Investigation Result

All three seeded issues are already fixed in the current application. The
before-state is documented in
`homework-4/context/bugs/001-order-receipt/bug-context.md:13`; the context
identifies the fixed calculation entry point at
`homework-4/context/bugs/001-order-receipt/bug-context.md:38`.

## Problem Statements and Reproducible Symptoms

### BR-1: Discount percentage was formerly treated as a multiplier

**Before-state symptom.** The bug context says the initial calculation used the
percentage directly rather than dividing by 100
(`homework-4/context/bugs/001-order-receipt/bug-context.md:5` and
`homework-4/context/bugs/001-order-receipt/bug-context.md:6`). Its recorded
reproduction—price `19.99`, quantity `2`, discount `10`—produced a negative
total rather than `$35.98` (`homework-4/context/bugs/001-order-receipt/bug-context.md:26`
and `homework-4/context/bugs/001-order-receipt/bug-context.md:27`).

**Current reproduction.**
`calculate_total(Decimal("19.99"), 2, Decimal("10"))` returned `35.98`.
The regression test makes the same assertion at
`homework-4/tests/test_order.py:18` through
`homework-4/tests/test_order.py:21`.

**Matching current source** — `homework-4/src/order_receipt/order.py:22`:

```python
subtotal = unit_price * quantity
discount = subtotal * (discount_percent / ONE_HUNDRED)
return (subtotal - discount).quantize(CENT, rounding=ROUND_HALF_UP)
```

`ONE_HUNDRED` is defined as `Decimal("100")` at
`homework-4/src/order_receipt/order.py:8`; cents and half-up rounding are
defined at `homework-4/src/order_receipt/order.py:7` and applied at
`homework-4/src/order_receipt/order.py:24`. The rounding regression is at
`homework-4/tests/test_order.py:23` through
`homework-4/tests/test_order.py:26`.

**Likely historical root cause and affected behavior.** The documented
before-state expression treated a whole-number percentage as a fraction:

```python
subtotal = unit_price * quantity
total = subtotal - (subtotal * discount_percent)
```

This exact before-state evidence is at
`homework-4/context/bugs/001-order-receipt/bug-context.md:18` and
`homework-4/context/bugs/001-order-receipt/bug-context.md:19`. Any nonzero
discount expressed as a normal percentage was affected; values above `1` could
subtract more than the subtotal.

### BR-2: Invalid quantities and numeric business values were formerly accepted

**Before-state symptom.** The bug context states that the seeded code had no
quantity, price, or discount validation
(`homework-4/context/bugs/001-order-receipt/bug-context.md:23`) and records
that quantity `-1` was accepted
(`homework-4/context/bugs/001-order-receipt/bug-context.md:28`).

**Current reproduction.** Calls with quantities `0` and `-1` each raised
`ValueError: quantity must be positive`. The regression loop covers both cases
at `homework-4/tests/test_order.py:28` through
`homework-4/tests/test_order.py:32`.

**Matching current source** — `homework-4/src/order_receipt/order.py:15`:

```python
if unit_price <= 0:
    raise ValueError("unit price must be positive")
if quantity <= 0:
    raise ValueError("quantity must be positive")
if not Decimal("0") <= discount_percent <= ONE_HUNDRED:
    raise ValueError("discount must be between 0 and 100")
```

The price and discount-bound regression tests are at
`homework-4/tests/test_order.py:34` through
`homework-4/tests/test_order.py:44`. The CLI passes parsed values to this
boundary at `homework-4/src/order_receipt/cli.py:36` through
`homework-4/src/order_receipt/cli.py:41`; its invalid-quantity integration test
is at `homework-4/tests/test_cli.py:55` through
`homework-4/tests/test_cli.py:71`.

**Likely historical root cause and affected behavior.** Arithmetic occurred
without business-rule validation, as the context records at
`homework-4/context/bugs/001-order-receipt/bug-context.md:23`. Zero and
negative quantities could yield meaningless totals; nonpositive prices and
discounts outside the required `0`–`100` range were likewise unguarded.

### BR-3: Customer-controlled receipt text was formerly unescaped

**Before-state symptom.** The bug context says customer input was directly
interpolated into receipt content that might be rendered as HTML
(`homework-4/context/bugs/001-order-receipt/bug-context.md:9` through
`homework-4/context/bugs/001-order-receipt/bug-context.md:11`). It records
that `<script>alert("x")</script>` was returned unchanged
(`homework-4/context/bugs/001-order-receipt/bug-context.md:29`).

**Current reproduction.** Rendering that name returned
`Customer: &lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;` before the total. The
unit assertion for the encoded name is at
`homework-4/tests/test_order.py:48` through
`homework-4/tests/test_order.py:53`.

**Matching current source** — `homework-4/src/order_receipt/order.py:27`:

```python
def safe_customer_name(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("customer name is required")
    return escape(normalized, quote=True)

def render_receipt(customer_name: str, total: Decimal) -> str:
    return f"Customer: {safe_customer_name(customer_name)}\nTotal: ${total:.2f}"
```

`escape` is imported from the standard-library HTML module at
`homework-4/src/order_receipt/order.py:4`. Blank-name validation is tested at
`homework-4/tests/test_order.py:55` through
`homework-4/tests/test_order.py:57`, and rendering an ampersand safely is
tested at `homework-4/tests/test_order.py:59` through
`homework-4/tests/test_order.py:62`.

**Likely historical root cause and affected behavior.** The before-state
returned customer input directly in the receipt template, shown at
`homework-4/context/bugs/001-order-receipt/bug-context.md:20`. An HTML-capable
consumer could interpret HTML-significant customer input, affecting every
receipt with unencoded customer-controlled characters.

## Root Causes

- **BR-1:** Whole-number percentages were used as decimal fractions in the
  documented before-state calculation
  (`homework-4/context/bugs/001-order-receipt/bug-context.md:19`).
- **BR-2:** The documented before state omitted domain validation before
  arithmetic (`homework-4/context/bugs/001-order-receipt/bug-context.md:23`).
- **BR-3:** The documented before state directly interpolated customer input
  into receipt output (`homework-4/context/bugs/001-order-receipt/bug-context.md:20`).

## References

- `homework-4/context/bugs/001-order-receipt/bug-context.md:5`
- `homework-4/context/bugs/001-order-receipt/bug-context.md:23`
- `homework-4/context/bugs/001-order-receipt/bug-context.md:38`
- `homework-4/src/order_receipt/order.py:15`
- `homework-4/src/order_receipt/order.py:23`
- `homework-4/src/order_receipt/order.py:32`
- `homework-4/src/order_receipt/order.py:37`
- `homework-4/src/order_receipt/cli.py:36`
- `homework-4/tests/test_order.py:18`
- `homework-4/tests/test_order.py:28`
- `homework-4/tests/test_order.py:48`
- `homework-4/tests/test_cli.py:55`

## Commands Used

Commands were run from the repository root:

```text
git status --short -- homework-4
rg --files homework-4/context/bugs/001-order-receipt homework-4
sed -n '1,260p' homework-4/context/bugs/001-order-receipt/bug-context.md
nl -ba homework-4/context/bugs/001-order-receipt/bug-context.md
nl -ba homework-4/src/order_receipt/order.py
nl -ba homework-4/src/order_receipt/cli.py
nl -ba homework-4/tests/test_order.py
nl -ba homework-4/tests/test_cli.py
git log --all --oneline -- homework-4/src/order_receipt homework-4/tests
git show d89cd73:homework-4/src/order_receipt/order.py
PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY' ... PY
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s homework-4/tests -v
```

The direct Python reproduction returned `35.98`, rejected quantities `0` and
`-1` with `quantity must be positive`, and encoded the hostile customer name.
The unittest command completed successfully: **26 tests passed**.
