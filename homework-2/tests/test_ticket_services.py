from support_tickets.services import import_ticket_records
from support_tickets.store import TicketStore


def valid_record(**overrides):
    record = {
        "customer_id": "cust-service",
        "customer_email": "service@example.com",
        "customer_name": "Service User",
        "subject": "Cannot access account",
        "description": "I cannot access my account after changing my password.",
        "metadata": {
            "source": "api",
            "browser": "Chrome",
            "device_type": "desktop",
        },
        "tags": ["service"],
    }
    record.update(overrides)
    return record


def test_import_ticket_records_creates_valid_records_and_reports_failures():
    store = TicketStore()

    summary = import_ticket_records(
        [
            valid_record(customer_email="valid@example.com"),
            valid_record(customer_email="invalid-email", description="short"),
        ],
        store,
    )

    assert summary.total_records == 2
    assert summary.successful == 1
    assert summary.failed == 1
    assert summary.errors[0].record_number == 2
    assert len(store.list()) == 1


def test_import_ticket_records_can_auto_classify_created_records():
    store = TicketStore()

    summary = import_ticket_records([valid_record()], store, auto_classify=True)

    ticket = store.get(summary.created_ticket_ids[0])
    assert ticket is not None
    assert ticket.category == "account_access"
    assert ticket.priority == "urgent"
    assert ticket.classification_confidence is not None
