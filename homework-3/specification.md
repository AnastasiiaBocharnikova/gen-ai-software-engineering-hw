# Virtual Card Lifecycle Management Specification

> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

Build a regulated virtual card lifecycle capability that lets verified customers create, freeze, unfreeze, limit, and review virtual cards while giving internal operations and compliance staff auditable tools to monitor risky activity.

Scope boundary: this specification covers the product, policy, data, verification, and implementation requirements for virtual card lifecycle management, but it does not require actual source code, APIs, UI screens, or production infrastructure for this homework.

## Stakeholders

- End-users: verified customers who create and manage virtual cards for spending.
- Internal operations: staff who investigate customer issues, processor failures, and lifecycle history.
- Compliance reviewers: staff who inspect suspicious patterns, audit trails, and policy controls.
- Fraud/risk analysts: staff or automated systems that identify abnormal card behavior.
- Engineering implementers: developers and Codex agents who will later turn this specification into code.

## Mid-Level Objectives

| ID | Objective | Observable outcome |
| --- | --- | --- |
| M1 | Card creation | A verified customer can request one virtual card and receive a tokenized card reference, masked display data, status, and creation timestamp. |
| M2 | Card lifecycle controls | A customer can freeze or unfreeze an eligible card, and internal compliance can place a hold that the customer cannot override. |
| M3 | Spending limits | A customer can set card spending limits that are valid, currency-aware, and enforceable before authorization decisions. |
| M4 | Transaction visibility | A customer and authorized internal staff can view paginated virtual card transactions with clear pending, settled, reversed, and declined states. |
| M5 | Auditability | Every sensitive action produces an immutable audit event with actor, reason, correlation ID, timestamp, and redacted metadata. |
| M6 | Regulated access boundaries | End-user, ops, compliance, and system actors only see and perform actions allowed by their role. |
| M7 | Resilience and reconciliation | Processor timeouts, retries, stale reads, and partial failures are visible, recoverable, and reconcilable. |

## Non-Functional and Policy Requirements

| Area | Requirement |
| --- | --- |
| Security | Never store or log full PAN, CVV, raw processor secrets, auth tokens, or unredacted card payloads. |
| Privacy | Show only masked card data such as `**** 4242`; expose full sensitive data only through a dedicated PCI-scoped provider flow outside this feature. |
| Authorization | Fail closed when the actor role, customer ownership, or compliance status is uncertain. |
| Audit | Sensitive lifecycle actions must emit immutable audit events before the action is reported as successful. |
| Reliability | Lifecycle writes must be idempotent by client request ID for at least 24 hours. |
| Consistency | Customer-facing reads should reflect successful lifecycle writes within 2 seconds under normal operation. |
| Performance | Assumed p95 latency target is 500 ms for freeze/unfreeze and 900 ms for card creation, excluding external processor degradation. |
| Availability | Customer lifecycle controls should target 99.9% monthly availability for the application tier. |
| Compliance | Compliance hold state must override customer unfreeze requests and must be retained in audit history. |
| Data retention | Audit events should be retained for 7 years unless the regulated environment requires a longer period. |

Performance numbers are assumed targets for this homework. They are reasonable because card controls are customer-trust workflows: freeze and unfreeze should feel near-immediate, while card creation may require a processor call and can tolerate slightly higher latency.

## Implementation Notes

- Use tokenized identifiers for cards, transactions, customers, and actors.
- Use fixed-point decimal money representation; never use binary floating point for monetary amounts.
- Store money as amount plus ISO 4217 currency, for example `amount_minor=1250`, `currency=USD`.
- Treat card status as an explicit state machine: `requested`, `active`, `frozen`, `compliance_hold`, `closed`, `processor_pending`, `failed`.
- Customer freeze/unfreeze may only move between `active` and `frozen`.
- Compliance hold may be applied from `active` or `frozen`; only compliance may remove it.
- All write operations must accept a client-generated idempotency key.
- Errors must be structured and safe to log: `error_code`, `message`, `correlation_id`, and optional redacted `details`.
- Do not expose whether another customer's card exists through error messages.
- Use cursor-based pagination for transaction history.
- External processor payloads must be normalized before entering application logs, audit records, or support tools.
- Audit event writes are part of the lifecycle definition of done, not a background nice-to-have.
- Fraud-ish patterns, such as rapid card creation or repeated limit changes, must be visible to risk/compliance workflows.

## Context

### Beginning Context

- `homework-3/TASKS.md` exists and defines the assignment.
- `homework-3/specification-TEMPLATE-example.md` exists and provides a basic layered format.
- No implementation code exists for this homework.
- The future implementation is hypothetical and may include an API service, database, card processor integration, customer UI, ops UI, and compliance review workflow.
- The intended AI coding partner is Codex.

### Ending Context

- `homework-3/specification.md` defines the full virtual card lifecycle feature.
- `homework-3/agents.md` defines Codex agent behavior for this FinTech domain.
- `homework-3/.codex/rules.md` defines Codex-specific AI/editor rules.
- `homework-3/README.md` explains the homework, rationale, best practices, and where each practice appears.
- A future implementer can decompose work without guessing about objectives, policy constraints, failure behavior, or verification criteria.

## Traceability Matrix

| Low-level task | M1 | M2 | M3 | M4 | M5 | M6 | M7 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1 Domain model and state machine | X | X | X | X | X | X | X |
| T2 Actor roles and permissions |  | X |  | X | X | X |  |
| T3 Card creation request | X |  |  |  | X | X | X |
| T4 Card creation idempotency | X |  |  |  | X |  | X |
| T5 Freeze/unfreeze lifecycle |  | X |  |  | X | X | X |
| T6 Compliance hold lifecycle |  | X |  |  | X | X | X |
| T7 Spending limit validation |  |  | X |  | X | X |  |
| T8 Authorization-time limit semantics |  |  | X |  | X |  | X |
| T9 Transaction history model |  |  |  | X | X | X | X |
| T10 Customer transaction view |  |  |  | X |  | X |  |
| T11 Ops/compliance transaction view |  |  |  | X | X | X |  |
| T12 Audit event contract | X | X | X | X | X | X | X |
| T13 Error handling and redaction | X | X | X | X | X | X | X |
| T14 Reconciliation workflow | X | X |  | X | X |  | X |
| T15 Verification fixtures | X | X | X | X | X | X | X |
| T16 Performance and rate-limit checks | X | X | X | X |  | X | X |

## Edge Cases and Failure Modes

| Scenario | Expected user-visible behavior | Audit/compliance implication |
| --- | --- | --- |
| Empty card list | Customer sees an empty state with an option to create a card if eligible. | No audit event required for read-only empty state. |
| Duplicate card creation retry | Return the original card result for the same idempotency key. | Audit records one creation plus any retry metadata, not duplicate cards. |
| Processor timeout during creation | Show pending status if the request may still complete; otherwise show safe failure with correlation ID. | Create reconciliation item and audit processor uncertainty. |
| Customer tries to unfreeze compliance-held card | Reject with a generic policy message. | Audit denied action with actor, card token, and reason code. |
| Concurrent freeze and unfreeze requests | Apply optimistic concurrency or ordered state transition; return latest known state. | Audit both attempts and final state. |
| Invalid limit below zero | Reject validation before persistence. | Audit not required unless policy requires tracking repeated abuse. |
| Limit exceeds product maximum | Reject with allowed range and currency. | Audit denied limit change with safe metadata. |
| Currency mismatch on limit | Reject with supported card currency. | Audit denied limit change if persisted attempt reaches service boundary. |
| Transaction list has no items | Show empty history with card status and pagination metadata. | No audit event required for customer read. |
| Stale transaction data | Show data freshness timestamp and allow retry. | Reconciliation job checks processor totals against internal records. |
| Unauthorized ops access | Return access denied without revealing card details. | Audit denied access attempt. |
| Rapid card creation pattern | Throttle or require review after policy threshold. | Create risk signal and compliance review item. |
| Audit write failure | Do not report lifecycle write success. | Raise operational alert because audit is mandatory. |
| Card already closed | Reject freeze, unfreeze, and limit changes. | Audit denied lifecycle action with closed-state reason. |

## Verification Strategy

| Objective | Verification approach |
| --- | --- |
| M1 Card creation | Review state machine, idempotency fixtures, processor timeout cases, and masked response examples. |
| M2 Card lifecycle controls | Verify allowed and denied state transitions, including customer freeze/unfreeze and compliance hold override. |
| M3 Spending limits | Verify numeric boundaries, currency mismatch handling, product maximums, and authorization-time enforcement notes. |
| M4 Transaction visibility | Verify pagination, role-specific visibility, empty states, stale data indicators, and transaction state definitions. |
| M5 Auditability | Verify every sensitive low-level task includes audit acceptance criteria and redacted event fields. |
| M6 Regulated access boundaries | Review role matrix, denied access cases, and safe error semantics. |
| M7 Resilience and reconciliation | Verify timeout behavior, retry semantics, reconciliation checkpoints, and operational alert criteria. |

Recommended future test categories:

- Unit tests for state transitions, limit validation, money formatting, and permission checks.
- Integration tests for card creation, lifecycle changes, audit persistence, and transaction pagination.
- End-to-end tests for customer create/freeze/unfreeze and ops compliance review flows.
- Negative tests for unauthorized access, invalid limits, stale versions, duplicate idempotency keys, and closed cards.
- Performance tests for p95 lifecycle latency, rate limits, and transaction pagination.
- Compliance review checklist for redaction, audit completeness, and retention expectations.

## Expected Performance Targets

| Flow | Assumed target | Reason |
| --- | --- | --- |
| Create virtual card | p95 under 900 ms when processor is healthy | Creation may require external card processor coordination. |
| Freeze or unfreeze card | p95 under 500 ms | Customers expect fast card safety controls. |
| Set spending limit | p95 under 600 ms | Limit changes are safety-sensitive and should feel immediate. |
| List transactions | p95 under 700 ms for first page of 50 items | Transaction history should support support calls and customer review. |
| Audit event persistence | p95 under 300 ms inside lifecycle write | Audit must complete before success is returned. |
| Read-after-write consistency | Customer reads reflect successful lifecycle write within 2 seconds | Avoid confusion after freeze, unfreeze, or limit update. |
| Rate limit | Maximum 5 card creations per customer per rolling hour unless approved | Reduces abuse and processor cost exposure. |
| Pagination | Default 25 transactions, maximum 100 per page | Protects service latency and predictable UI behavior. |

## Low-Level Tasks

### T1. Define Domain Model and State Machine

What prompt would you run to complete this task?
Define the virtual card domain entities, status values, valid state transitions, and money representation for a regulated virtual card lifecycle service.

What file do you want to CREATE or UPDATE?
Hypothetical implementation file: `src/virtual_cards/domain.py`

What function/class do you want to CREATE or UPDATE?
`VirtualCard`, `CardStatus`, `Money`, `Transaction`, `CardStateMachine`

What details drive the change?
- Represent card IDs as tokenized IDs.
- Represent money as minor units plus ISO currency.
- Define statuses: `requested`, `active`, `frozen`, `compliance_hold`, `closed`, `processor_pending`, `failed`.
- Prevent direct customer transitions into or out of `compliance_hold`.
- Acceptance criteria:
  - All status transitions are listed and testable.
  - Invalid transitions produce structured errors.
  - No field requires storing PAN or CVV.

### T2. Define Actor Roles and Permissions

What prompt would you run to complete this task?
Create a permission matrix for customers, ops staff, compliance staff, fraud systems, and processors for all virtual card lifecycle actions.

What file do you want to CREATE or UPDATE?
Hypothetical implementation file: `src/virtual_cards/permissions.py`

What function/class do you want to CREATE or UPDATE?
`ActorRole`, `can_create_card`, `can_change_card_status`, `can_view_transactions`, `can_apply_compliance_hold`

What details drive the change?
- Customers may manage only their own eligible cards.
- Ops may view operational metadata but not full sensitive card data.
- Compliance may place and remove compliance holds.
- Fraud systems may create risk signals but not expose customer-sensitive details.
- Acceptance criteria:
  - Unauthorized actions fail closed.
  - Denied actions do not reveal whether another customer's card exists.
  - Permission decisions can be audited with actor and reason.

### T3. Specify Card Creation Request Flow

What prompt would you run to complete this task?
Design the card creation flow from customer request through eligibility, processor provisioning, tokenized response, and audit event.

What file do you want to CREATE or UPDATE?
Hypothetical implementation file: `src/virtual_cards/create_card.py`

What function/class do you want to CREATE or UPDATE?
`create_virtual_card(customer_id, request, actor, idempotency_key)`

What details drive the change?
- Validate customer eligibility before processor call.
- Return masked card data only.
- Support pending status when processor result is uncertain.
- Acceptance criteria:
  - Successful creation returns tokenized card ID, masked display value, status, and timestamp.
  - Ineligible customers receive a safe, structured error.
  - Success is not returned unless audit event persistence succeeds.

### T4. Specify Idempotency for Card Creation

What prompt would you run to complete this task?
Add idempotency semantics for card creation to prevent duplicate virtual cards during client retries or network failures.

What file do you want to CREATE or UPDATE?
Hypothetical implementation file: `src/virtual_cards/idempotency.py`

What function/class do you want to CREATE or UPDATE?
`IdempotencyRecord`, `get_or_create_idempotent_result`

What details drive the change?
- Key uniqueness is scoped to customer ID plus idempotency key plus operation type.
- Store completed response or recoverable pending state for 24 hours.
- Reject key reuse with incompatible request payload.
- Acceptance criteria:
  - Same key and same payload returns original result.
  - Same key and different payload returns conflict.
  - Duplicate processor calls are avoided when a completed result exists.

### T5. Specify Customer Freeze and Unfreeze

What prompt would you run to complete this task?
Design customer-controlled freeze and unfreeze operations with state validation, concurrency control, and audit events.

What file do you want to CREATE or UPDATE?
Hypothetical implementation file: `src/virtual_cards/lifecycle.py`

What function/class do you want to CREATE or UPDATE?
`freeze_card(card_id, actor, idempotency_key)`, `unfreeze_card(card_id, actor, idempotency_key)`

What details drive the change?
- Freeze only `active` cards.
- Unfreeze only `frozen` cards.
- Reject closed, failed, pending, or compliance-held cards.
- Use version checks or ordered state transition processing for concurrent requests.
- Acceptance criteria:
  - Frozen cards cannot authorize new transactions.
  - Denied unfreeze from compliance hold returns a policy-safe message.
  - Every accepted or denied sensitive transition creates an audit event.

### T6. Specify Compliance Hold Lifecycle

What prompt would you run to complete this task?
Design compliance hold placement and removal for virtual cards, including reason capture, customer visibility, and audit requirements.

What file do you want to CREATE or UPDATE?
Hypothetical implementation file: `src/virtual_cards/compliance.py`

What function/class do you want to CREATE or UPDATE?
`apply_compliance_hold(card_id, compliance_actor, reason_code)`, `remove_compliance_hold(card_id, compliance_actor, reason_code)`

What details drive the change?
- Only compliance actors can place or remove holds.
- Hold reason codes must come from an approved list.
- Customers may see limited policy messaging, not investigation details.
- Acceptance criteria:
  - Customer unfreeze cannot override compliance hold.
  - Hold placement and removal are audit events with reason codes.
  - Closed cards cannot be reactivated by removing a hold.

### T7. Specify Spending Limit Validation

What prompt would you run to complete this task?
Design customer spending limit validation for amount, currency, period, product maximum, and card status.

What file do you want to CREATE or UPDATE?
Hypothetical implementation file: `src/virtual_cards/limits.py`

What function/class do you want to CREATE or UPDATE?
`set_spending_limit(card_id, limit_request, actor, idempotency_key)`, `validate_limit(limit_request, card)`

What details drive the change?
- Limit amount must be positive.
- Currency must match the card's billing currency.
- Supported periods are `daily`, `weekly`, `monthly`, and `per_transaction`.
- Product maximums must be enforced before persistence.
- Acceptance criteria:
  - Invalid limits return structured validation errors.
  - Limit changes on closed or compliance-held cards are denied.
  - Accepted limit changes create audit events.

### T8. Specify Authorization-Time Limit Semantics

What prompt would you run to complete this task?
Define how spending limits affect authorization decisions and what happens when transaction data or limit state is stale.

What file do you want to CREATE or UPDATE?
Hypothetical implementation file: `src/virtual_cards/authorization_policy.py`

What function/class do you want to CREATE or UPDATE?
`evaluate_authorization(card_id, authorization_request)`

What details drive the change?
- Decline authorizations when the card is frozen, closed, failed, or compliance-held.
- Decline transactions that exceed per-transaction or period limits.
- Prefer fail-closed if required limit state is unavailable.
- Acceptance criteria:
  - Limit evaluation uses fixed-point money.
  - Decline reasons are safe and do not expose internal risk details.
  - Authorization decisions reference the card and limit versions used.

### T9. Specify Transaction History Model

What prompt would you run to complete this task?
Define normalized transaction records and transaction states for customer and internal virtual card history views.

What file do you want to CREATE or UPDATE?
Hypothetical implementation file: `src/virtual_cards/transactions.py`

What function/class do you want to CREATE or UPDATE?
`Transaction`, `TransactionStatus`, `normalize_processor_transaction`

What details drive the change?
- Supported statuses are `pending`, `settled`, `reversed`, and `declined`.
- Store merchant name only after sanitization.
- Preserve processor reference IDs in restricted internal metadata.
- Acceptance criteria:
  - Customer records contain no raw processor payload.
  - Internal records include enough metadata for reconciliation.
  - Transaction timestamps include timezone-aware UTC values.

### T10. Specify Customer Transaction View

What prompt would you run to complete this task?
Design the customer transaction history view with cursor pagination, empty state, freshness timestamp, and safe card ownership checks.

What file do you want to CREATE or UPDATE?
Hypothetical implementation file: `src/virtual_cards/customer_transactions.py`

What function/class do you want to CREATE or UPDATE?
`list_customer_card_transactions(customer_id, card_id, cursor, page_size)`

What details drive the change?
- Default page size is 25, maximum is 100.
- Customer can only view their own card transactions.
- Response includes `data_fresh_as_of`.
- Acceptance criteria:
  - Empty transaction history returns an empty list and pagination metadata.
  - Unauthorized card access returns access denied without confirming ownership details.
  - Stale data is visible through freshness metadata.

### T11. Specify Ops and Compliance Transaction View

What prompt would you run to complete this task?
Design internal transaction search and review for authorized ops and compliance actors with restricted metadata and audit logging.

What file do you want to CREATE or UPDATE?
Hypothetical implementation file: `src/virtual_cards/internal_review.py`

What function/class do you want to CREATE or UPDATE?
`search_internal_transactions(actor, filters, cursor, page_size)`, `get_card_audit_timeline(actor, card_id)`

What details drive the change?
- Ops may search by tokenized customer ID, tokenized card ID, status, and date range.
- Compliance may view risk reason codes and hold history.
- Internal reads of sensitive records should be audited when policy requires.
- Acceptance criteria:
  - Internal views never reveal PAN or CVV.
  - Search filters are bounded to prevent broad data scraping.
  - Compliance-only metadata is hidden from ops-only actors.

### T12. Specify Audit Event Contract

What prompt would you run to complete this task?
Define the immutable audit event contract for all sensitive virtual card actions.

What file do you want to CREATE or UPDATE?
Hypothetical implementation file: `src/virtual_cards/audit.py`

What function/class do you want to CREATE or UPDATE?
`AuditEvent`, `record_audit_event`

What details drive the change?
- Required fields: event ID, actor ID, actor role, action, resource token, reason code, correlation ID, timestamp, and redacted metadata.
- Audit events are append-only.
- Audit write failure blocks lifecycle success responses.
- Acceptance criteria:
  - Every sensitive task names its audit action.
  - Metadata redaction is enforced before persistence.
  - Audit events can be filtered by resource token and correlation ID.

### T13. Specify Error Handling and Redaction

What prompt would you run to complete this task?
Create a standard error model and redaction policy for virtual card lifecycle failures.

What file do you want to CREATE or UPDATE?
Hypothetical implementation file: `src/virtual_cards/errors.py`

What function/class do you want to CREATE or UPDATE?
`VirtualCardError`, `redact_sensitive_fields`, `safe_error_response`

What details drive the change?
- Error response shape: `error_code`, `message`, `correlation_id`, `details`.
- Details must be safe for logs and customer support tooling.
- Raw processor messages must be mapped to internal reason codes.
- Acceptance criteria:
  - Full PAN, CVV, raw token, and secrets are removed from errors.
  - Permission errors do not leak resource existence.
  - Correlation IDs appear in customer-safe error responses.

### T14. Specify Reconciliation Workflow

What prompt would you run to complete this task?
Design reconciliation for processor pending states, transaction mismatches, duplicate requests, and stale card statuses.

What file do you want to CREATE or UPDATE?
Hypothetical implementation file: `src/virtual_cards/reconciliation.py`

What function/class do you want to CREATE or UPDATE?
`reconcile_pending_card_creations`, `reconcile_transactions`, `create_reconciliation_case`

What details drive the change?
- Pending card creations older than 5 minutes require processor lookup.
- Transaction totals should reconcile by processor reference and card token.
- Unresolved mismatches create internal cases.
- Acceptance criteria:
  - Reconciliation creates audit or operational events with correlation IDs.
  - Reconciliation does not expose raw processor payloads.
  - Stale pending states are resolved or escalated within defined time windows.

### T15. Specify Verification Fixtures

What prompt would you run to complete this task?
Define fixture data for valid and invalid virtual card lifecycle scenarios that future tests and reviews can reuse.

What file do you want to CREATE or UPDATE?
Hypothetical files: `sample_data/valid/virtual_card_cases.json`, `sample_data/invalid/virtual_card_cases.json`

What function/class do you want to CREATE or UPDATE?
No function; fixture contract only.

What details drive the change?
- Valid fixtures include active card, frozen card, pending transaction, settled transaction, and valid limit.
- Invalid fixtures include negative limit, currency mismatch, unauthorized actor, closed card action, and compliance-held unfreeze.
- Acceptance criteria:
  - Fixtures contain tokenized IDs only.
  - Each invalid fixture maps to an expected error code.
  - Each valid fixture maps to one or more mid-level objectives.

### T16. Specify Performance and Rate-Limit Checks

What prompt would you run to complete this task?
Define performance, rate-limit, and load verification requirements for the virtual card lifecycle service.

What file do you want to CREATE or UPDATE?
Hypothetical file: `tests/performance/test_virtual_card_slos.py`

What function/class do you want to CREATE or UPDATE?
`test_freeze_unfreeze_p95_latency`, `test_card_creation_rate_limit`, `test_transaction_pagination_limit`

What details drive the change?
- Freeze/unfreeze p95 under 500 ms.
- Card creation p95 under 900 ms when processor stub is healthy.
- Transaction list default 25 and maximum 100.
- Customer card creation limit is 5 per rolling hour.
- Acceptance criteria:
  - Performance tests use realistic fixture volumes.
  - Rate-limit tests verify both allowed and denied requests.
  - Results are documented with assumed environment limits.
