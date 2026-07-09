from datetime import datetime

from support_tickets.models import TicketCreate
from support_tickets.store import TicketStore


def valid_ticket_payload(**overrides):
    payload = {
        "customer_id": "cust-123",
        "customer_email": "customer@example.com",
        "customer_name": "Ada Lovelace",
        "subject": "Cannot access account",
        "description": "I cannot access my account after resetting my password.",
        "metadata": {
            "source": "web_form",
            "browser": "Chrome",
            "device_type": "desktop",
        },
        "tags": ["login"],
    }
    payload.update(overrides)
    return payload


def make_ticket(**overrides):
    return TicketCreate(**valid_ticket_payload(**overrides))


def test_create_stores_ticket_with_generated_id_and_timestamps():
    store = TicketStore()

    ticket = store.create(make_ticket())

    assert ticket.id
    assert isinstance(ticket.created_at, datetime)
    assert ticket.updated_at == ticket.created_at
    assert store.get(ticket.id) == ticket


def test_list_returns_tickets_in_creation_order():
    store = TicketStore()
    first = store.create(make_ticket(customer_email="first@example.com"))
    second = store.create(make_ticket(customer_email="second@example.com"))

    assert store.list() == [first, second]


def test_list_filters_by_category_priority_and_status():
    store = TicketStore()
    matching = store.create(
        make_ticket(
            category="billing_question",
            priority="high",
            status="in_progress",
            customer_email="billing@example.com",
        )
    )
    store.create(make_ticket(category="technical_issue", priority="high"))
    store.create(make_ticket(category="billing_question", priority="low"))

    tickets = store.list(
        category="billing_question",
        priority="high",
        status="in_progress",
    )

    assert tickets == [matching]


def test_update_changes_only_provided_fields_and_refreshes_updated_at():
    store = TicketStore()
    ticket = store.create(make_ticket())

    updated = store.update(
        ticket.id,
        {
            "subject": "Updated subject",
            "priority": "urgent",
            "tags": ["login", "urgent"],
        },
    )

    assert updated is not None
    assert updated.subject == "Updated subject"
    assert updated.priority == "urgent"
    assert updated.customer_email == ticket.customer_email
    assert updated.tags == ["login", "urgent"]
    assert updated.updated_at > ticket.updated_at


def test_update_marks_classification_overridden_when_manual_category_changes():
    store = TicketStore()
    ticket = store.create(make_ticket(category="other"))

    updated = store.update(ticket.id, {"category": "account_access"})

    assert updated is not None
    assert updated.category == "account_access"
    assert updated.classification_overridden is True


def test_update_does_not_mark_override_when_category_and_priority_are_unchanged():
    store = TicketStore()
    ticket = store.create(make_ticket(category="account_access", priority="urgent"))
    classified = store.apply_classification(
        ticket.id,
        category="account_access",
        priority="urgent",
        confidence=0.9,
        reasoning="Matched existing classification.",
        keywords=["password"],
    )

    updated = store.update(
        ticket.id,
        {
            "category": "account_access",
            "priority": "urgent",
            "assigned_to": "agent-1",
        },
    )

    assert classified is not None
    assert updated is not None
    assert updated.assigned_to == "agent-1"
    assert updated.classification_overridden is False


def test_update_sets_resolved_at_when_status_becomes_resolved():
    store = TicketStore()
    ticket = store.create(make_ticket())

    updated = store.update(ticket.id, {"status": "resolved"})

    assert updated is not None
    assert updated.status == "resolved"
    assert updated.resolved_at is not None


def test_delete_removes_existing_ticket_and_reports_missing_ids():
    store = TicketStore()
    ticket = store.create(make_ticket())

    assert store.delete(ticket.id) is True
    assert store.get(ticket.id) is None
    assert store.delete(ticket.id) is False


def test_reset_clears_all_tickets():
    store = TicketStore()
    store.create(make_ticket())

    store.reset()

    assert store.list() == []
