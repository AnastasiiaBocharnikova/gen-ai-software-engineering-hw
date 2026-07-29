# Unit Test Report

## Changed-Code Scope

`fix-summary.md` confirms that no source or regression-test files changed in
this execution because the verified behavior was already present. The existing
regressions cover the changed behavior at:

- `homework-4/src/order_receipt/order.py:15` — positive price and quantity,
  plus inclusive `0`–`100` discount validation.
- `homework-4/src/order_receipt/order.py:23` — percentage conversion and
  half-up cent rounding.
- `homework-4/src/order_receipt/order.py:29` — normalized, escaped customer
  names.
- `homework-4/src/order_receipt/cli.py:36` — conversion of business validation
  errors to exit status `2`.

## Tests Generated

No tests were added or modified: the current focused regressions already cover
each verified changed behavior, and adding duplicates would not test a new
behavior.

- `homework-4/tests/test_order.py:18` and
  `homework-4/tests/test_order.py:23` cover percentage discounting and
  half-up currency rounding.
- `homework-4/tests/test_order.py:28`, `homework-4/tests/test_order.py:34`,
  and `homework-4/tests/test_order.py:38` cover rejected business values.
- `homework-4/tests/test_order.py:48`, `homework-4/tests/test_order.py:55`,
  and `homework-4/tests/test_order.py:59` cover escaping, blank names, and
  safe receipt output.
- `homework-4/tests/test_cli.py:55` covers the validation-error status and
  message at the CLI boundary.

## FIRST Assessment

- **Fast — PASS:** the focused suite completed 11 tests in `0.001s`; the full
  suite completed 26 tests in `0.005s`. Tests use in-process functions and no
  network calls or sleeps.
- **Independent — PASS:** each test supplies its own `Decimal` inputs and, for
  CLI tests, creates fresh `StringIO` output captures. No test relies on order
  or shared mutable state.
- **Repeatable — PASS:** expected values are fixed `Decimal` values and strings;
  the tests do not use time, randomness, locale, network services, or external
  filesystem state.
- **Self-validating — PASS:** `unittest` equality, containment, and exception
  assertions determine success automatically; no manual output inspection is
  needed.
- **Timely — PASS:** existing regressions directly cover the verified
  calculation, validation, escaping, and CLI-error behavior. Since no behavior
  changed in this execution, no new test was appropriate.

## Test Results

Focused command (run from `homework-4/`):

```bash
python3 -B -m unittest tests.test_order tests.test_cli -v
```

Result: **PASS — Ran 11 tests in 0.001s; OK.**

Full command (run from `homework-4/`):

```bash
python3 -m unittest discover -s tests -v
```

Result: **PASS — Ran 26 tests in 0.005s; OK.**

Coverage: unavailable in the current execution environment. `requirements.txt`
declares `coverage>=7.6,<8`, but `python3 -m coverage --version` returned
`No module named coverage`; no coverage percentage is reported rather than
using the pre-existing `.coverage` file of unknown provenance.
