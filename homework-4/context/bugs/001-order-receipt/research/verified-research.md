# Verified Research

## Verification Summary

**PASS — Research Quality: GOOD.** All 31 material claim, snippet, command, and
conclusion groups in `codebase-research.md` were checked against the current
repository: 29 verified and 2 had minor documentation discrepancies. All 42
distinct repository-relative `file:line` citations resolve and support the
associated claims in context. The discrepancies do not change the identified
defects, root causes, current behavior, or safe planning direction.

## Verified Claims

1. The bug context identifies three seeded issues: incorrect percentage
   discounting, invalid quantities, and unescaped customer input
   (`homework-4/context/bugs/001-order-receipt/bug-context.md:5`,
   `homework-4/context/bugs/001-order-receipt/bug-context.md:7`,
   `homework-4/context/bugs/001-order-receipt/bug-context.md:9`).
2. The documented before state begins at
   `homework-4/context/bugs/001-order-receipt/bug-context.md:13`, and the context
   identifies the current calculation entry point at
   `homework-4/context/bugs/001-order-receipt/bug-context.md:38`.
3. The context says the initial discount calculation used
   `discount_percent` directly instead of dividing by 100
   (`homework-4/context/bugs/001-order-receipt/bug-context.md:5` through
   `homework-4/context/bugs/001-order-receipt/bug-context.md:6`).
4. The recorded price `19.99`, quantity `2`, and discount `10` symptom and
   expected `$35.98` are present exactly as claimed
   (`homework-4/context/bugs/001-order-receipt/bug-context.md:26` through
   `homework-4/context/bugs/001-order-receipt/bug-context.md:27`).
5. Independent execution of `calculate_total(Decimal("19.99"), 2,
   Decimal("10"))` returned `Decimal("35.98")`; the same assertion is at
   `homework-4/tests/test_order.py:18` through
   `homework-4/tests/test_order.py:21`.
6. The BR-1 current-source snippet is exact: it calculates the subtotal,
   divides the percentage by `ONE_HUNDRED`, subtracts the discount, and
   quantizes the result (`homework-4/src/order_receipt/order.py:22` through
   `homework-4/src/order_receipt/order.py:24`).
7. `CENT` is `Decimal("0.01")`, `ONE_HUNDRED` is `Decimal("100")`, and
   `ROUND_HALF_UP` is applied during quantization
   (`homework-4/src/order_receipt/order.py:7`,
   `homework-4/src/order_receipt/order.py:8`,
   `homework-4/src/order_receipt/order.py:24`).
8. The half-up rounding regression is present at
   `homework-4/tests/test_order.py:23` through
   `homework-4/tests/test_order.py:26`.
9. The quoted BR-1 before-state snippet exactly matches
   `homework-4/context/bugs/001-order-receipt/bug-context.md:18` through
   `homework-4/context/bugs/001-order-receipt/bug-context.md:19`.
10. The BR-1 affected-behavior conclusion follows mathematically from the
    before-state expression: any ordinary nonzero percentage is treated as a
    fraction, and a value above `1` subtracts more than the subtotal
    (`homework-4/context/bugs/001-order-receipt/bug-context.md:19`).
11. The context records missing quantity, price, and discount validation and
    acceptance of quantity `-1`
    (`homework-4/context/bugs/001-order-receipt/bug-context.md:23`,
    `homework-4/context/bugs/001-order-receipt/bug-context.md:28`).
12. Independent calls with quantities `0` and `-1` both raised
    `ValueError("quantity must be positive")`; the regression covers both
    values at `homework-4/tests/test_order.py:28` through
    `homework-4/tests/test_order.py:32`.
13. The BR-2 current-source snippet is exact: price and quantity must be
    positive, and discount must be inclusively between zero and 100
    (`homework-4/src/order_receipt/order.py:15` through
    `homework-4/src/order_receipt/order.py:20`).
14. The nonpositive-price and out-of-range-discount regressions are present at
    `homework-4/tests/test_order.py:34` through
    `homework-4/tests/test_order.py:44`.
15. The CLI passes parsed price, quantity, and discount values to
    `calculate_total`, then converts validation failures to status `2`
    (`homework-4/src/order_receipt/cli.py:36` through
    `homework-4/src/order_receipt/cli.py:41`).
16. The CLI invalid-business-value regression supplies quantity `0` and checks
    status `2` plus the quantity error
    (`homework-4/tests/test_cli.py:55` through
    `homework-4/tests/test_cli.py:71`).
17. The BR-2 root-cause and affected-behavior conclusions are supported by the
    documented absence of business validation
    (`homework-4/context/bugs/001-order-receipt/bug-context.md:23`) and the
    current pre-arithmetic guards
    (`homework-4/src/order_receipt/order.py:15`).
18. The context says customer input was directly interpolated into content
    that may be rendered as HTML, enabling XSS in an HTML consumer
    (`homework-4/context/bugs/001-order-receipt/bug-context.md:9` through
    `homework-4/context/bugs/001-order-receipt/bug-context.md:11`).
19. The hostile input and its unchanged before-state result are recorded at
    `homework-4/context/bugs/001-order-receipt/bug-context.md:29`.
20. Independent rendering of `<script>alert("x")</script>` produced
    `Customer: &lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;`, followed by
    `Total: $35.98`; the encoded-name assertion is at
    `homework-4/tests/test_order.py:48` through
    `homework-4/tests/test_order.py:53`.
21. `safe_customer_name` strips input, rejects a blank normalized value, and
    calls `escape(normalized, quote=True)`
    (`homework-4/src/order_receipt/order.py:27` through
    `homework-4/src/order_receipt/order.py:32`).
22. `escape` is imported from the standard-library `html` module
    (`homework-4/src/order_receipt/order.py:4`), and `render_receipt` calls
    `safe_customer_name` before formatting the total
    (`homework-4/src/order_receipt/order.py:35` through
    `homework-4/src/order_receipt/order.py:37`).
23. Blank-name rejection and ampersand-safe rendering are tested at
    `homework-4/tests/test_order.py:55` through
    `homework-4/tests/test_order.py:62`.
24. The BR-3 root-cause conclusion follows from direct before-state
    interpolation
    (`homework-4/context/bugs/001-order-receipt/bug-context.md:20`) and current
    boundary escaping (`homework-4/src/order_receipt/order.py:29` through
    `homework-4/src/order_receipt/order.py:32`).
25. The three root-cause summary bullets accurately restate the evidence at
    `homework-4/context/bugs/001-order-receipt/bug-context.md:19`,
    `homework-4/context/bugs/001-order-receipt/bug-context.md:23`, and
    `homework-4/context/bugs/001-order-receipt/bug-context.md:20`.
26. Every path and line in the research References section resolves to the
    cited current file and supports the surrounding research claim, including
    `homework-4/src/order_receipt/order.py:23`,
    `homework-4/src/order_receipt/order.py:32`, and
    `homework-4/src/order_receipt/order.py:37`.
27. The reported repository inspection commands (`git status`, `rg --files`,
    `sed`, the five `nl -ba` commands, `git log`, and `git show`) execute
    successfully from the repository root. The scoped log contains commits
    `dde9f74` and `d89cd73`, and `d89cd73` contains the current fixed
    `order.py`.
28. The three stated direct-reproduction outcomes were independently
    confirmed: total `35.98`, rejection of quantities `0` and `-1` with
    `quantity must be positive`, and HTML encoding of the hostile customer
    name.
29. The reported unittest discovery command was rerun exactly and completed
    successfully with **26 tests passed**.

## Discrepancies Found

1. The BR-3 quoted source block is not character-for-character exact. It omits
   the function docstrings present at
   `homework-4/src/order_receipt/order.py:28` and
   `homework-4/src/order_receipt/order.py:36` without marking the omissions.
   All quoted executable statements match the source in their correct order,
   so this is a minor snippet-transcription issue.
2. The listed direct Python command is abbreviated as
   `python3 -B - <<'PY' ... PY`; its exact body cannot be reproduced from the
   research artifact. All three claimed outcomes were independently reproduced,
   so this is a command-documentation gap rather than unsupported behavioral
   evidence.

## Research Quality Assessment

**GOOD.** Twenty-nine of 31 checked groups verified (93.5%). Every material
behavior, root-cause conclusion, test assertion, and all 42 distinct
repository-relative references are supported. The two explicit discrepancies
are minor and do not change a proposed fix or prevent a safe implementation
plan. The research is not `EXCELLENT` because that level requires exact
snippets and complete command evidence. It is well above `UNRELIABLE`, so Stage
2 passes.

## References

- `homework-4/agents/research-verifier.agent.md`
- `homework-4/skills/research-quality-measurement.md`
- `homework-4/context/bugs/001-order-receipt/research/codebase-research.md`
- `homework-4/context/bugs/001-order-receipt/bug-context.md`
- `homework-4/src/order_receipt/order.py`
- `homework-4/src/order_receipt/cli.py`
- `homework-4/tests/test_order.py`
- `homework-4/tests/test_cli.py`
- `homework-4/tests/test_pipeline_contract.py`
- Git object `d89cd73:homework-4/src/order_receipt/order.py`
