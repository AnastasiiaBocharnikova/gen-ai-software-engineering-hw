# Order Receipt Bug Fix Implementation Plan

## Files and Locations

Verified research status: **PASS — Research Quality: GOOD**. The current
repository already contains the verified fixes and regressions, so execution
starts with tests and makes no source or test edit when they pass.

- `homework-4/tests/test_order.py:18-26` verifies percentage discounting and
  half-up cent rounding.
- `homework-4/tests/test_order.py:28-44` verifies rejection of non-positive
  quantities and prices and discounts outside the inclusive `0` through `100`
  range.
- `homework-4/tests/test_order.py:48-62` verifies hostile-name escaping,
  blank-name rejection, and safe receipt rendering.
- `homework-4/tests/test_cli.py:15-35` verifies the complete valid order path,
  including an escaped customer name and the `$35.98` total.
- `homework-4/tests/test_cli.py:55-71` verifies that a business-validation
  failure returns status `2` and writes the quantity error.
- `homework-4/src/order_receipt/order.py:7-24` contains the constants,
  validation, percentage calculation, and currency rounding that would be
  modified only if their focused regressions fail because this exact logic is
  absent.
- `homework-4/src/order_receipt/order.py:27-37` contains customer-name
  normalization, validation, HTML escaping, and receipt rendering that would be
  modified only if their focused regressions fail because this exact logic is
  absent.
- `homework-4/src/order_receipt/cli.py:36-43` already delegates calculation and
  rendering to `order.py` and converts `ValueError` to status `2`; verify this
  path without editing it.

Run all Python commands below from `homework-4/`. Do not recreate a vulnerable
before-state to force a red test, and do not edit files merely to reproduce the
documented defects.

## Before and After Behavior

- Percentage discounting:
  - Before: the subtotal was multiplied directly by `discount_percent`; price
    `19.99`, quantity `2`, and discount `10` produced a negative total.
  - After: divide the percentage by `Decimal("100")`, subtract the resulting
    discount, and quantize to `Decimal("0.01")` with `ROUND_HALF_UP`; the same
    inputs return `Decimal("35.98")`.
- Business-value validation:
  - Before: price, quantity, and discount had no business validation, and
    quantity `-1` was accepted.
  - After: reject prices and quantities less than or equal to zero and reject
    discounts below `0` or above `100` before arithmetic. The CLI reports the
    `ValueError` and returns status `2`.
- Customer-controlled receipt text:
  - Before: `<script>alert("x")</script>` was interpolated unchanged into
    receipt content that may be rendered as HTML.
  - After: strip surrounding whitespace, reject an empty normalized name, and
    apply `html.escape(..., quote=True)` before interpolation. The hostile name
    becomes `&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;`.

## Test-First Changes

### 1. Percentage calculation and rounding

1. Confirm the two existing regressions at
   `homework-4/tests/test_order.py:18-26` assert `Decimal("35.98")` for the
   documented order and `Decimal("0.05")` for the half-up rounding case.
2. Run the two-test command in `Test Commands`.
3. If both tests pass, record this task as already satisfied and make no edit.
4. Only if either test fails because the verified calculation is absent, make
   the minimal change at `homework-4/src/order_receipt/order.py:7-8` and
   `homework-4/src/order_receipt/order.py:22-24`: retain
   `CENT = Decimal("0.01")` and `ONE_HUNDRED = Decimal("100")`, calculate
   `subtotal * (discount_percent / ONE_HUNDRED)`, subtract it from the subtotal,
   and quantize with `ROUND_HALF_UP`.
5. Re-run the same two-test command; do not continue if it is not green.

### 2. Order-value validation

1. Confirm the regressions at `homework-4/tests/test_order.py:28-44` cover
   quantities `0` and `-1`, price `0`, and discounts `-1` and `101`. Confirm
   `homework-4/tests/test_cli.py:55-71` checks status `2` and
   `quantity must be positive`.
2. Run the four-test command in `Test Commands`.
3. If all four tests pass, record this task as already satisfied and make no
   edit.
4. Only if a test fails because the verified guards are absent, add the minimal
   pre-arithmetic checks at `homework-4/src/order_receipt/order.py:15-20`:
   `unit_price <= 0` raises `ValueError("unit price must be positive")`,
   `quantity <= 0` raises `ValueError("quantity must be positive")`, and a
   discount outside `0 <= discount_percent <= ONE_HUNDRED` raises
   `ValueError("discount must be between 0 and 100")`.
5. Keep the delegation and error conversion at
   `homework-4/src/order_receipt/cli.py:36-43` unchanged, then re-run the same
   four-test command; do not continue if it is not green.

### 3. Safe customer-name rendering

1. Confirm the regressions at `homework-4/tests/test_order.py:48-62` assert the
   encoded hostile value, reject a whitespace-only name, and render
   `Ada &amp; Co` with `Total: $35.98`.
2. Run the three-test command in `Test Commands`.
3. If all three tests pass, record this task as already satisfied and make no
   edit.
4. Only if a test fails because the verified boundary handling is absent, make
   the minimal change at `homework-4/src/order_receipt/order.py:4` and
   `homework-4/src/order_receipt/order.py:27-37`: import `html.escape`, strip the
   value, raise `ValueError("customer name is required")` when it is blank,
   return `escape(normalized, quote=True)`, and have `render_receipt` interpolate
   the helper result.
5. Preserve the CLI `try` block at `homework-4/src/order_receipt/cli.py:36-41`
   so name validation follows the existing status-`2` path. Re-run the same
   three-test command; do not continue if it is not green.

### 4. Already-satisfied completion gate

1. Run the combined focused suite and the full suite in `Test Commands`.
2. If both pass with the exact counts below, make no source or test changes.
3. Inspect the scoped diff. For the verified current tree, execution of this
   plan must add no diff to `order.py`, `cli.py`, `test_order.py`, or
   `test_cli.py`.

## Test Commands

From `homework-4/`, run:

```bash
python3 -B -m unittest \
  tests.test_order.CalculateTotalTests.test_applies_percentage_discount \
  tests.test_order.CalculateTotalTests.test_rounds_currency_half_up -v
```

```bash
python3 -B -m unittest \
  tests.test_order.CalculateTotalTests.test_rejects_non_positive_quantity \
  tests.test_order.CalculateTotalTests.test_rejects_non_positive_price \
  tests.test_order.CalculateTotalTests.test_rejects_discount_outside_zero_to_one_hundred \
  tests.test_cli.CliTests.test_returns_error_for_invalid_business_value -v
```

```bash
python3 -B -m unittest \
  tests.test_order.ReceiptTests.test_escapes_untrusted_customer_name \
  tests.test_order.ReceiptTests.test_rejects_blank_customer_name \
  tests.test_order.ReceiptTests.test_renders_safe_receipt -v
```

```bash
python3 -B -m unittest tests.test_order tests.test_cli -v
```

```bash
python3 -B -m unittest discover -s tests -v
```

From the repository root, inspect only the planned implementation scope:

```bash
git diff -- \
  homework-4/src/order_receipt/order.py \
  homework-4/src/order_receipt/cli.py \
  homework-4/tests/test_order.py \
  homework-4/tests/test_cli.py
```

## Expected Results

- The percentage and rounding command reports `Ran 2 tests` and `OK`.
- The validation command reports `Ran 4 tests` and `OK`; the CLI regression
  observes status `2` and `quantity must be positive`.
- The safe-rendering command reports `Ran 3 tests` and `OK`; the hostile name is
  HTML-encoded and the rendered ampersand is `&amp;`.
- The combined focused suite reports `Ran 11 tests` and `OK`. Its valid CLI
  regression expects `Customer: Ada &amp; Co`, followed by `Total: $35.98`.
- The full suite reports `Ran 26 tests` and `OK`.
- Because the current source and tests already satisfy every verified claim,
  the scoped source/test diff remains unchanged and no implementation patch is
  required.
- Stop without editing source or tests if the research status is no longer
  `PASS`, its quality becomes `UNRELIABLE`, a failure is unrelated to one of
  the three verified defects, the exact minimal change does not make its
  focused command pass, or the full-suite count/result differs from the
  expected 26 passing tests. Report the mismatch for renewed research instead
  of broadening the fix.
