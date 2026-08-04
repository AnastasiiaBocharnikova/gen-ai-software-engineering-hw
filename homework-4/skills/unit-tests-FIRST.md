# FIRST Unit Tests

Use this skill when generating or reviewing unit tests for new or changed code.
Apply all five FIRST principles and record evidence for each one in
`test-report.md`.

## Core Rule

Generate the smallest deterministic tests that prove changed behavior. A test
must be capable of failing when the intended change is absent or broken.

Do not change production behavior to make a weak test pass. Do not add tests for
unchanged code only to increase coverage.

## Acceptance Criteria

| Principle | Pass criteria | Failure signals |
| --- | --- | --- |
| **Fast** | Focused unit tests complete in under one second locally when practical; the test uses no network call, arbitrary sleep, retry delay, or heavyweight service startup. | `sleep`, real HTTP/database calls, slow process startup, or a focused test that takes seconds without evidence that the cost is unavoidable. |
| **Independent** | A test passes alone, in the full suite, and in a different execution order; it creates and cleans up its own state. | Shared mutable globals, reliance on a previous test, fixed shared files, or order-dependent assertions. |
| **Repeatable** | Identical code and inputs produce the same result across runs and supported environments. Time, randomness, locale, environment variables, and external services are controlled. | Current clock, unseeded randomness, machine-specific paths, locale-dependent formatting, or live external data. |
| **Self-validating** | Assertions determine success automatically and explain the expected behavior. No human must inspect logs, screenshots, or printed values. | “Run and check output manually,” assertions without meaningful expectations, or tests that only prove no exception occurred. |
| **Timely** | Tests are created with the changed behavior and cover only its public outcome, boundary conditions, failure modes, and regression risk. | Tests added after implementation without a demonstrated regression, tests coupled to private details, or unrelated coverage padding. |

If a criterion cannot be met, document the exception, evidence, risk, and
mitigation in `test-report.md`. An unexplained exception fails the assessment.

## Risk-Based Test Selection

Read `fix-summary.md` and changed files before selecting cases. Map each changed
behavior to the smallest relevant set:

| Risk | Add a test when | Required evidence |
| --- | --- | --- |
| Happy path | The primary successful behavior changed. | Exact input and observable result. |
| boundary value | Validation, ranges, rounding, limits, or empty values changed. | Values immediately inside, on, and outside the boundary where relevant. |
| Invalid input | New validation or parsing was added. | Expected exception, error shape, message, or status. |
| security regression | Encoding, authorization, secrets, injection, or unsafe input handling changed. | A harmless adversarial input proving the vulnerability remains blocked. |
| error propagation | A lower-layer failure is translated or returned by the changed code. | Exact public error behavior without relying on logs. |
| State transition | The change creates, updates, or removes state. | State before and after, with isolated setup and cleanup. |

Do not create every category mechanically. Select only categories connected to
the changed behavior and explain omissions when the risk is material.

## Generation Workflow

1. **Identify scope**
   - Read `fix-summary.md` completely.
   - List changed production files and observable behaviors.
   - Exclude unrelated modules.
2. **Inspect the existing test style**
   - Use the project's framework, naming, fixtures, and assertion conventions.
   - Prefer public interfaces over implementation details.
3. **Choose cases by risk**
   - Apply the selection matrix.
   - Use one focused test per behavior or failure mode.
4. **Prove RED**
   - Run the new test against the missing or broken behavior when safe.
   - Confirm it fails for the expected reason, not because of a typo or setup
     error.
   - If the repository already contains the fixed state and recreating the bug
     would be unsafe, cite the before-state evidence and explain the proof gap.
5. **Make the test pass**
   - Add only the setup and assertions needed to prove the behavior.
   - Never weaken production validation or expose private internals for a test.
6. **Check FIRST explicitly**
   - Run the test alone.
   - Run the relevant test file or class.
   - Run the complete suite.
   - Re-run focused tests when time, ordering, or shared state could matter.
7. **Record results**
   - Write commands, counts, duration, changed-code scope, coverage if
     available, and evidence for every FIRST principle to `test-report.md`.

## Good Example

This Python `unittest` case is focused, deterministic, and proves both a
security boundary and the public output:

```python
from decimal import Decimal
import unittest

from order_receipt.order import render_receipt


class ReceiptSecurityTests(unittest.TestCase):
    def test_escapes_customer_markup_in_receipt(self) -> None:
        receipt = render_receipt("<script>alert(1)</script>", Decimal("9.99"))

        self.assertEqual(
            receipt,
            "Customer: &lt;script&gt;alert(1)&lt;/script&gt;\nTotal: $9.99",
        )
```

Why it satisfies FIRST:

- **Fast**: pure in-memory code with no waits or external services.
- **Independent**: no shared state or dependency on another test.
- **Repeatable**: fixed inputs and no clock, randomness, or environment access.
- **Self-validating**: one exact assertion defines the expected result.
- **Timely**: directly protects the changed output-encoding behavior.

## Bad Example

```python
def test_receipt():
    time.sleep(2)
    customer = requests.get("https://example.com/current-customer").text
    print(render_receipt(customer, Decimal("9.99")))
```

Violations:

- **Fast** fails because of the sleep and network request.
- **Independent** fails because an external service controls the input.
- **Repeatable** fails because remote data and availability can change.
- **Self-validating** fails because output is printed without an assertion.
- **Timely** cannot be demonstrated because the expected changed behavior is
  unspecified.

## Anti-Patterns

| Anti-pattern | Why it fails | Correction |
| --- | --- | --- |
| Real network or database in a unit test | Slow and nondeterministic. | Test a pure boundary or inject a small deterministic fake. |
| Arbitrary `sleep` | Adds delay without proving readiness. | Call synchronous logic directly or wait on an observable condition in an integration test. |
| Shared fixture mutated by multiple tests | Creates order dependence. | Create fresh state in each test and clean it locally. |
| Current time or unseeded random data | Produces run-dependent results. | Inject a clock/value or use fixed deterministic inputs. |
| Testing private method calls | Couples the test to implementation. | Assert the public result, state change, or error. |
| “No exception” as the only assertion | Does not define correct behavior. | Assert the exact return value, state, or error contract. |
| Snapshot or log requiring human inspection | Not self-validating. | Assert the relevant structured values automatically. |
| Tests for unchanged code to raise coverage | Violates changed-code scope. | Trace every new test to a changed behavior in `fix-summary.md`. |
| Modifying production code solely for test access | Distorts the design. | Test through an existing public boundary or improve design only when required by product behavior. |

## Required test-report.md Template

Use these exact top-level sections:

```markdown
# Unit Test Report

## Changed-Code Scope

- `path/to/file.py:line` — observable behavior covered
- Explicit exclusions and reasoning

## Tests Generated

| Test | Behavior/risk | Result |
| --- | --- | --- |
| `test_name` | happy path, boundary, invalid input, security regression, or error propagation | PASS/FAIL |

## Test Results

- Focused command: `<command>`
- Focused result: `<count, status, duration>`
- Full command: `<command>`
- Full result: `<count, status, duration>`
- Coverage: `<value and command, or unavailable with reason>`

## FIRST Assessment

- **Fast**: PASS/FAIL — measured evidence
- **Independent**: PASS/FAIL — isolation/order evidence
- **Repeatable**: PASS/FAIL — controlled-dependency evidence
- **Self-validating**: PASS/FAIL — assertion evidence
- **Timely**: PASS/FAIL — link to changed behavior

## Exceptions and Mitigations

- `None`, or criterion, evidence, risk, and mitigation

## Overall Status

- PASS/FAIL and unresolved test gaps

## References

- `fix-summary.md`
- changed source and test `file:line` references
```

## Completion Checklist

- [ ] Every generated test maps to a changed behavior in `fix-summary.md`.
- [ ] Relevant happy path, boundary, invalid input, security regression, and
      error propagation risks were considered.
- [ ] Each new regression test demonstrated RED, or the safe proof gap is
      documented.
- [ ] Focused tests pass.
- [ ] The complete suite passes.
- [ ] Tests use no uncontrolled network, time, randomness, locale, environment,
      or shared mutable state.
- [ ] Assertions validate exact public behavior.
- [ ] Every FIRST principle has evidence in `test-report.md`.
- [ ] Coverage is recorded when available; unrelated tests were not added to
      inflate it.

## Stop Conditions

Stop and report `FAIL` instead of claiming completion when:

- a focused or full-suite test fails;
- a new test passes without exercising the intended changed behavior;
- the required changed file or `fix-summary.md` is missing;
- a test depends on an unavailable external system;
- production behavior would need to be weakened only to satisfy the test;
- a FIRST exception lacks evidence and mitigation;
- the generated test targets unchanged code without a documented regression
  relationship.
