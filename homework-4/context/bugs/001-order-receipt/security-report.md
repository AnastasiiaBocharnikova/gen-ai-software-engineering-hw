# Security Report

## Scope

Reviewed the implementation and regression coverage referenced by
`homework-4/context/bugs/001-order-receipt/fix-summary.md`:

- `homework-4/src/order_receipt/order.py:11`
- `homework-4/src/order_receipt/cli.py:20`
- `homework-4/tests/test_order.py:17`
- `homework-4/tests/test_cli.py:14`
- `homework-4/requirements.txt:1`

No source, test, configuration, or dependency file was edited.

## Checks Performed

- **Injection:** checked customer-controlled receipt interpolation and the CLI
  path; no shell, SQL, template, or dynamic-code execution sink is present.
- **Hardcoded secrets:** checked scoped source and dependency files; no
  credentials, tokens, or private keys are present.
- **Insecure comparisons:** checked conditional logic; no authentication,
  authorization, token, or other secret comparison is present.
- **Input validation:** verified positive price and quantity checks, the
  inclusive `0` through `100` discount bound, nonblank customer-name
  validation, and CLI handling of invalid numeric and business values.
- **Unsafe dependencies:** runtime code uses only the Python standard library.
  The sole declared third-party package is the test-only coverage tool, bounded
  to major version 7; the reviewed fix adds no dependency.
- **XSS:** verified HTML encoding occurs before customer-controlled text is
  interpolated into the receipt.
- **CSRF:** not applicable because the reviewed application is a local CLI with
  no HTTP endpoint, browser session, cookie, or state-changing web request.

## Findings

No open findings.

## Resolved Seeded Issue

### INFO — Customer-name XSS risk resolved

- **File:** `homework-4/src/order_receipt/order.py:32`
- **Evidence:** `safe_customer_name` applies `html.escape(..., quote=True)`;
  `homework-4/src/order_receipt/order.py:37` uses that encoded value for
  receipt interpolation. The hostile-name regression at
  `homework-4/tests/test_order.py:48` passes.
- **Impact:** customer-supplied markup such as a `<script>` element is emitted
  as encoded text instead of executable HTML when the receipt is consumed as
  HTML.
- **Remediation:** none required. Retain the encoding boundary and regression
  coverage.

## Overall Status

**PASS — No open findings.** The seeded XSS issue is resolved and
regression-tested.
