# Fix Summary

## Changes Made

No source or regression-test files were changed: every planned after-state was
already satisfied, so no seeded issue was reintroduced.

- Percentage calculation and rounding: before, the seeded behavior used the
  percentage as a direct multiplier; after, `homework-4/src/order_receipt/order.py:23`
  divides by `ONE_HUNDRED` and `homework-4/src/order_receipt/order.py:24`
  applies half-up cent rounding. The regressions at
  `homework-4/tests/test_order.py:18` and `homework-4/tests/test_order.py:23`
  passed (2 tests, `OK`). **Already satisfied.**
- Order-value validation: before, non-positive values and out-of-range discounts
  were accepted; after, `homework-4/src/order_receipt/order.py:15` validates
  business values and `homework-4/src/order_receipt/cli.py:39` converts a
  `ValueError` to status `2`. The regressions at
  `homework-4/tests/test_order.py:28`, `homework-4/tests/test_order.py:34`,
  `homework-4/tests/test_order.py:38`, and `homework-4/tests/test_cli.py:55`
  passed (4 tests, `OK`). **Already satisfied.**
- Safe customer-name rendering: before, customer text was interpolated without
  escaping; after, `homework-4/src/order_receipt/order.py:29` normalizes the
  name, `homework-4/src/order_receipt/order.py:32` escapes it, and
  `homework-4/src/order_receipt/order.py:37` renders the safe value. The
  regressions at `homework-4/tests/test_order.py:48`,
  `homework-4/tests/test_order.py:55`, and `homework-4/tests/test_order.py:59`
  passed (3 tests, `OK`). **Already satisfied.**

## Overall Status

**COMPLETE.** The combined focused suite passed: 11 tests, `OK`. The full
suite passed: 26 tests, `OK`. The scoped diff contains no changes to
`homework-4/src/order_receipt/order.py:11`,
`homework-4/src/order_receipt/cli.py:20`,
`homework-4/tests/test_order.py:17`, or
`homework-4/tests/test_cli.py:14`.

## Manual Verification

From `homework-4/`, run:

```bash
PYTHONPATH=src python3 -m order_receipt.cli \
  --customer "Ada & Co" --price 19.99 --quantity 2 --discount 10
```

Expected output:

```text
Customer: Ada &amp; Co
Total: $35.98
```

For the validation path, run:

```bash
PYTHONPATH=src python3 -m order_receipt.cli \
  --customer Ada --price 10 --quantity 0
```

Expected: exit status `2` and `error: quantity must be positive` on stderr.

## References

- Plan: `homework-4/context/bugs/001-order-receipt/implementation-plan.md`
- Changed file: `homework-4/context/bugs/001-order-receipt/fix-summary.md`
- Verified implementation: `homework-4/src/order_receipt/order.py:15`,
  `homework-4/src/order_receipt/order.py:23`, and
  `homework-4/src/order_receipt/order.py:29`; CLI path:
  `homework-4/src/order_receipt/cli.py:36`.
- Regression tests: `homework-4/tests/test_order.py:18`,
  `homework-4/tests/test_order.py:28`,
  `homework-4/tests/test_order.py:48`, and
  `homework-4/tests/test_cli.py:55`.
