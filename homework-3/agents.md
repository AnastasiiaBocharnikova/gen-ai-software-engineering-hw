# Codex Agent Guidelines for Homework 3

These guidelines apply to Codex when working on the Homework 3 virtual card lifecycle specification package.

## Scope

- Treat this homework as documentation-only unless the user explicitly changes the assignment.
- Keep all homework-specific files inside `homework-3/`.
- Do not create implementation code, API routes, UI files, migrations, or test files for this homework.
- Preserve `TASKS.md` and `specification-TEMPLATE-example.md` as assignment inputs.

## Assumed Future Stack

- Backend service: Python with FastAPI or another explicit API framework chosen later.
- Persistence: relational database for card state, audit events, and reconciliation records.
- External dependency: card processor integration through a provider adapter.
- Testing: unit, integration, end-to-end, performance, and compliance review checks.
- Documentation: Markdown specifications, architecture notes, and verification checklists.

## Domain Rules

- Treat virtual cards as regulated financial instruments.
- Model lifecycle state explicitly; do not infer state from loosely related fields.
- Use tokenized IDs for cards, customers, transactions, actors, and processor references.
- Use fixed-point decimal or minor-unit integer representation for money.
- Store money with ISO 4217 currency.
- Prefer idempotent writes for create, freeze, unfreeze, limit changes, and compliance actions.
- Define beginning context, ending context, acceptance criteria, and failure behavior for each implementable task.

## Security and Privacy Rules

- Never log or persist full PAN, CVV, raw auth tokens, secrets, or unredacted processor payloads.
- Mask card display values, for example `**** 4242`.
- Fail closed when authorization, ownership, or role data is missing or uncertain.
- Do not reveal whether another customer's card exists.
- Redact sensitive fields before writing logs, audit events, support views, or error details.
- Keep PCI-scoped card reveal flows outside this homework unless explicitly requested.

## Compliance and Audit Rules

- Treat auditability as a core requirement, not an optional implementation detail.
- Every sensitive action must define its audit event fields.
- Audit events must include actor, role, action, resource token, reason or result, correlation ID, timestamp, and redacted metadata.
- Compliance holds override customer lifecycle actions.
- Only compliance actors may remove compliance holds.
- Retain audit history in a way suitable for regulated review.

## Edge Case Rules

- Explicitly cover empty states, duplicate requests, processor timeouts, stale data, concurrent lifecycle actions, invalid limits, permission failures, and suspicious behavior.
- For each important edge case, state customer-visible behavior and audit/compliance behavior.
- Prefer structured errors with safe messages and correlation IDs.
- Do not use vague phrases such as "handle errors" without naming the expected behavior.

## Testing and Verification Expectations

- Tie verification back to mid-level objectives.
- Include unit, integration, end-to-end, negative, performance, and compliance review categories where relevant.
- Define fixture expectations for valid and invalid data.
- Include acceptance criteria or definition of done for low-level tasks.
- Use measurable targets for performance, rate limits, consistency, and pagination.

## Writing Style

- Be specific, concise, and implementation-ready.
- Prefer tables for traceability, edge cases, performance targets, and role permissions.
- Avoid generic security essays; keep controls tied to the virtual card feature.
- Write rules and requirements for Codex, not Copilot, Cursor, or Claude.
