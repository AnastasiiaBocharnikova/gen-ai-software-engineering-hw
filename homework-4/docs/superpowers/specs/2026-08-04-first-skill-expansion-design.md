# FIRST Skill Expansion Design

## Goal

Expand `skills/unit-tests-FIRST.md` from a minimal definition into a practical,
reasoning-oriented guide that the Unit Test Generator can apply consistently to
changed code and explain in `test-report.md`.

## Scope

Only the FIRST skill and its structural contract test will change. The agent
definitions, pipeline order, application behavior, and existing reports remain
unchanged unless verification reveals a direct compatibility issue.

## Structure

The expanded skill remains a single Markdown file, as required by `TASKS.md`.
It will contain:

1. Purpose and core rule.
2. Measurable acceptance criteria for Fast, Independent, Repeatable,
   Self-validating, and Timely.
3. A risk-based test-selection matrix covering happy paths, boundaries,
   invalid input, security regressions, and error propagation.
4. A step-by-step generation workflow from changed-code discovery through
   focused and full-suite verification.
5. One complete good Python `unittest` example.
6. One contrasting bad example with a FIRST violation analysis.
7. Common anti-patterns and concrete corrections.
8. An exact `test-report.md` template.
9. Completion and stop-condition checklists.

## Behavioral Requirements

- Tests target only new or changed behavior.
- Each regression test must be capable of failing without the intended change.
- Tests must avoid external networks, arbitrary sleeps, shared mutable state,
  uncontrolled clocks, randomness, locale, and manual result inspection.
- The generator must run focused tests before the complete suite.
- Production behavior must not be weakened to make a test pass.
- Coverage must not be inflated with unrelated tests.
- Any FIRST exception must be documented with evidence and mitigation.

## Validation

Before editing, a baseline evaluation will demonstrate that the current skill
does not require the richer criteria and report structure. After editing:

- structural tests will require the new sections and key concepts;
- the complete homework test suite will run;
- pipeline validation will run;
- the file will be checked for concise, internally consistent guidance and a
  usable report template.

## Acceptance Criteria

- The reviewer-requested depth is visible and actionable.
- All five FIRST principles have measurable pass/fail criteria.
- Good and bad examples show how to apply the criteria.
- The workflow, matrix, anti-patterns, report template, and checklists are
  complete.
- Existing homework tests and pipeline validation pass.
