import json

from fastapi.testclient import TestClient

from support_tickets.main import app, ticket_store


client = TestClient(app)


def setup_function():
    ticket_store.reset()


def valid_ticket_payload(**overrides):
    payload = {
        "customer_id": "cust-integration",
        "customer_email": "integration@example.com",
        "customer_name": "Integration User",
        "subject": "Cannot access account",
        "description": "I cannot access my account after changing my password.",
        "metadata": {
            "source": "web_form",
            "browser": "Chrome",
            "device_type": "desktop",
        },
        "tags": ["integration"],
    }
    payload.update(overrides)
    return payload


def test_complete_ticket_lifecycle_workflow():
    created = client.post("/tickets", json=valid_ticket_payload()).json()

    classified = client.post(f"/tickets/{created['id']}/auto-classify").json()
    assert classified["category"] == "account_access"

    updated_response = client.put(
        f"/tickets/{created['id']}",
        json={"status": "resolved", "assigned_to": "agent-lifecycle"},
    )
    assert updated_response.status_code == 200
    updated = updated_response.json()
    assert updated["status"] == "resolved"
    assert updated["resolved_at"] is not None

    fetched = client.get(f"/tickets/{created['id']}").json()
    assert fetched["assigned_to"] == "agent-lifecycle"

    delete_response = client.delete(f"/tickets/{created['id']}")
    assert delete_response.status_code == 204
    assert client.get(f"/tickets/{created['id']}").status_code == 404


def test_bulk_import_with_auto_classification_workflow():
    payload = [
        valid_ticket_payload(
            customer_email="access@example.com",
            subject="Critical password problem",
            description="I cannot access my login after changing my password.",
        ),
        valid_ticket_payload(
            customer_email="billing@example.com",
            subject="Invoice refund question",
            description="I need a refund for a duplicate payment.",
        ),
    ]

    response = client.post(
        "/tickets/import?format=json&auto_classify=true",
        files={"file": ("tickets.json", json.dumps(payload), "application/json")},
    )

    assert response.status_code == 201
    summary = response.json()
    assert summary["successful"] == 2
    tickets = client.get("/tickets").json()
    assert {ticket["customer_email"] for ticket in tickets} == {
        "access@example.com",
        "billing@example.com",
    }
    assert all(ticket["classification_confidence"] is not None for ticket in tickets)


def test_combined_filtering_by_category_and_priority():
    client.post(
        "/tickets",
        json=valid_ticket_payload(
            customer_email="match@example.com",
            category="billing_question",
            priority="high",
        ),
    )
    client.post(
        "/tickets",
        json=valid_ticket_payload(
            customer_email="wrong-category@example.com",
            category="technical_issue",
            priority="high",
        ),
    )
    client.post(
        "/tickets",
        json=valid_ticket_payload(
            customer_email="wrong-priority@example.com",
            category="billing_question",
            priority="low",
        ),
    )

    response = client.get("/tickets?category=billing_question&priority=high")

    assert response.status_code == 200
    assert [ticket["customer_email"] for ticket in response.json()] == ["match@example.com"]


def test_partial_import_then_manual_correction_workflow():
    payload = [
        valid_ticket_payload(customer_email="valid@example.com"),
        valid_ticket_payload(customer_email="invalid-email", description="short"),
    ]

    import_response = client.post(
        "/tickets/import?format=json",
        files={"file": ("tickets.json", json.dumps(payload), "application/json")},
    )

    assert import_response.status_code == 201
    summary = import_response.json()
    assert summary["successful"] == 1
    assert summary["failed"] == 1

    ticket_id = summary["created_ticket_ids"][0]
    update_response = client.put(
        f"/tickets/{ticket_id}",
        json={"category": "account_access", "priority": "high"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["classification_overridden"] is True


def test_filtering_after_import_and_classification_workflow():
    payload = [
        valid_ticket_payload(
            customer_email="urgent-access@example.com",
            subject="Critical password issue",
            description="I cannot access my login after changing my password.",
        ),
        valid_ticket_payload(
            customer_email="low-feature@example.com",
            subject="Suggestion for dashboard",
            description="Minor suggestion to add a better dashboard filter.",
        ),
    ]

    client.post(
        "/tickets/import?format=json&auto_classify=true",
        files={"file": ("tickets.json", json.dumps(payload), "application/json")},
    )

    response = client.get("/tickets?category=account_access&priority=urgent")

    assert response.status_code == 200
    assert [ticket["customer_email"] for ticket in response.json()] == [
        "urgent-access@example.com"
    ]
