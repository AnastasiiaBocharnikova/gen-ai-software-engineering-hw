import pytest
from pydantic import ValidationError

from support_tickets.models import (
    TicketCreate,
    TicketMetadata,
    TicketResponse,
    TicketUpdate,
)


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
        "tags": ["login", "password"],
    }
    payload.update(overrides)
    return payload


def test_ticket_create_accepts_valid_required_fields():
    ticket = TicketCreate(**valid_ticket_payload())

    assert ticket.customer_email == "customer@example.com"
    assert ticket.category == "other"
    assert ticket.priority == "medium"
    assert ticket.status == "new"
    assert ticket.assigned_to is None
    assert ticket.tags == ["login", "password"]


def test_ticket_create_rejects_invalid_email():
    with pytest.raises(ValidationError) as exc:
        TicketCreate(**valid_ticket_payload(customer_email="not-an-email"))

    assert "customer_email" in str(exc.value)


def test_ticket_create_rejects_subject_over_200_characters():
    with pytest.raises(ValidationError) as exc:
        TicketCreate(**valid_ticket_payload(subject="x" * 201))

    assert "subject" in str(exc.value)


def test_ticket_create_rejects_description_under_10_characters():
    with pytest.raises(ValidationError) as exc:
        TicketCreate(**valid_ticket_payload(description="too short"))

    assert "description" in str(exc.value)


def test_ticket_create_rejects_invalid_category_priority_and_status():
    with pytest.raises(ValidationError) as exc:
        TicketCreate(
            **valid_ticket_payload(
                category="wrong",
                priority="now",
                status="unknown",
            )
        )

    message = str(exc.value)
    assert "category" in message
    assert "priority" in message
    assert "status" in message


def test_ticket_metadata_rejects_invalid_source_and_device_type():
    with pytest.raises(ValidationError) as exc:
        TicketMetadata(source="fax", browser="Firefox", device_type="watch")

    message = str(exc.value)
    assert "source" in message
    assert "device_type" in message


def test_ticket_update_allows_partial_manual_override_fields():
    update = TicketUpdate(category="billing_question", priority="high")

    assert update.category == "billing_question"
    assert update.priority == "high"
    assert update.status is None


def test_ticket_response_generates_server_fields():
    ticket = TicketResponse.from_create(TicketCreate(**valid_ticket_payload()))

    assert ticket.id
    assert ticket.created_at
    assert ticket.updated_at
    assert ticket.resolved_at is None
    assert ticket.classification_confidence is None
    assert ticket.classification_keywords == []
    assert ticket.classification_overridden is False
