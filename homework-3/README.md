# Homework 3: Specification-Driven Design

## Student and Task Summary

Student: Anastasiia Bocharnikova

This homework defines a specification package for a finance-oriented application feature: virtual card lifecycle management. The package contains a layered product/engineering specification, Codex agent guidelines, Codex-specific AI rules, and this README.

No implementation code is required or included.

## Deliverables

- `specification.md`: layered specification for virtual card creation, freeze/unfreeze, spending limits, transaction visibility, auditability, and compliance review.
- `agents.md`: Codex agent guidelines for future implementation work in this FinTech domain.
- `.codex/rules.md`: Codex-specific editor/AI rules for maintaining this homework.
- `README.md`: rationale, summary, and industry practice mapping.

## Rationale

Virtual card lifecycle management was chosen because it is small enough to specify clearly but realistic enough to require regulated-system thinking. The feature naturally includes end-user workflows, internal operations workflows, compliance controls, audit requirements, sensitive data handling, idempotency, and processor failure modes.

The specification uses multiple layers so a future engineering team or Codex agent can move from intent to implementation without guessing:

- The high-level objective defines the business outcome and scope boundary.
- The mid-level objectives define observable outcomes.
- The non-functional requirements make security, privacy, audit, reliability, and performance measurable.
- The implementation notes capture guardrails that future builders must not violate.
- The beginning and ending context define the workspace and expected artifact state.
- The traceability matrix connects low-level tasks back to objectives.
- The low-level tasks provide implementable slices with acceptance criteria.

Performance targets are labeled as assumed targets because this homework does not include production telemetry. The numbers are still concrete so they can guide future design and testing. Freeze and unfreeze target p95 under 500 ms because customers use those controls to prevent unwanted spending. Card creation targets p95 under 900 ms because it may require an external processor call. Transaction pagination defaults and maximums are included to protect latency and operational usability.

Verification depth was chosen to match a regulated FinTech workflow. The spec includes unit, integration, end-to-end, negative, performance, reconciliation, and compliance review checks. This makes verification part of the specification instead of an afterthought.

## Industry Best Practices

| Practice | Where it appears |
| --- | --- |
| Tokenized card identifiers and masked display data | `specification.md` sections "Implementation Notes", "Low-Level Tasks T1, T3, T13"; `agents.md` sections "Domain Rules" and "Security and Privacy Rules" |
| No PAN, CVV, secret, or raw processor payload logging | `specification.md` sections "Non-Functional and Policy Requirements", "Implementation Notes", "Edge Cases and Failure Modes"; `.codex/rules.md` section "FinTech Defaults" |
| Idempotent lifecycle writes | `specification.md` sections "Non-Functional and Policy Requirements", "Low-Level Tasks T4, T5, T7"; `agents.md` section "Domain Rules" |
| Immutable audit events | `specification.md` sections "Non-Functional and Policy Requirements", "Low-Level Tasks T12"; `agents.md` section "Compliance and Audit Rules" |
| Fail-closed authorization | `specification.md` sections "Non-Functional and Policy Requirements", "Low-Level Tasks T2, T13"; `.codex/rules.md` section "FinTech Defaults" |
| Compliance hold override | `specification.md` sections "Implementation Notes", "Low-Level Tasks T6"; `agents.md` section "Compliance and Audit Rules" |
| Fixed-point money handling | `specification.md` sections "Implementation Notes", "Low-Level Tasks T1, T7, T8"; `.codex/rules.md` section "FinTech Defaults" |
| Explicit edge cases and failure behavior | `specification.md` section "Edge Cases and Failure Modes"; `agents.md` section "Edge Case Rules" |
| Measurable performance expectations | `specification.md` sections "Non-Functional and Policy Requirements" and "Expected Performance Targets" |
| Traceability from objectives to tasks | `specification.md` section "Traceability Matrix" |

## How to Review

1. Read `specification.md` from the objective through the low-level tasks.
2. Confirm each mid-level objective maps to one or more low-level tasks in the traceability matrix.
3. Review edge cases for customer-visible behavior and audit/compliance implications.
4. Review the performance targets and confirm they are measurable.
5. Review `agents.md` and `.codex/rules.md` to confirm the AI rules are specific to Codex.

## Project Structure

```text
homework-3/
├── README.md
├── TASKS.md
├── agents.md
├── specification.md
├── specification-TEMPLATE-example.md
└── .codex/
    └── rules.md
```
