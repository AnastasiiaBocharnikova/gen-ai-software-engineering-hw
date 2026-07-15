# Codex Rules for Homework 3

These rules are for Codex when editing or reviewing the Homework 3 specification package.

## Assignment Boundary

- Codex must keep this homework documentation-only.
- Codex must not create application source code, API handlers, UI components, database migrations, or executable tests unless the user explicitly changes the assignment.
- Codex must keep all new deliverables inside `homework-3/`.
- Codex must preserve the original task and template files.

## Required Deliverables

Codex should maintain these files:

- `homework-3/specification.md`
- `homework-3/agents.md`
- `homework-3/.codex/rules.md`
- `homework-3/README.md`

Codex must not satisfy this homework by creating Copilot, Cursor, or Claude rule files. The AI/editor rules for this homework are Codex-specific and live in `.codex/rules.md`.

## Specification Rules

- Start from the layered structure shown in `specification-TEMPLATE-example.md`, but replace placeholders with concrete virtual card lifecycle requirements.
- Include a high-level objective, mid-level objectives, non-functional requirements, implementation notes, beginning context, ending context, and low-level tasks.
- Include edge cases and failure modes inside the specification, not only in the README.
- Include verification expectations inside the specification, not only in the README.
- Include measurable performance targets inside the specification, not only in the README.
- Ensure low-level tasks trace back to mid-level objectives.

## FinTech Defaults

- Never log or expose full PAN, CVV, raw processor payloads, secrets, or auth tokens.
- Use tokenized IDs and masked card display values.
- Use fixed-point or minor-unit money representation with ISO currency.
- Require idempotency for lifecycle writes.
- Require immutable audit events for sensitive actions.
- Fail closed on authorization uncertainty.
- Treat compliance holds as stronger than customer-initiated lifecycle actions.

## Review Checklist

Before Codex says the work is complete, verify:

- The README explains why the specification is structured the way it is.
- Industry practices are mapped to specific sections or files.
- The agent rules are written for Codex.
- No generated implementation code exists for this homework.
- No unrelated homework folders were modified.
