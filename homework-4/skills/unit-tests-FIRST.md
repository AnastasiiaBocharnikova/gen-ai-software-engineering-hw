# FIRST Unit Tests

Use this skill when generating tests for changed code. Tests must assess all
five FIRST properties.

## Principles

- **Fast**: focused tests finish quickly and avoid network calls or sleeps.
- **Independent**: each test creates its own state and does not depend on order.
- **Repeatable**: results do not depend on time, randomness, locale, or external
  services.
- **Self-validating**: assertions determine pass or fail without manual review.
- **Timely**: tests are added with the changed behavior and target only the
  affected code.

## Generator Checklist

1. Read `fix-summary.md` and enumerate changed behaviors.
2. Follow the project's existing test framework and naming conventions.
3. Add the smallest tests that fail without each change.
4. Avoid testing unchanged modules merely to inflate coverage.
5. Run the focused tests and then the complete suite.
6. Record the command, result, duration, changed-code scope, and an explicit
   assessment of each FIRST property in `test-report.md`.
