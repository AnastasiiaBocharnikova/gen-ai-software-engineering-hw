from fastapi.testclient import TestClient

from support_tickets.main import app, ticket_store


client = TestClient(app)


def setup_function():
    ticket_store.reset()


def test_create_ticket_returns_201_and_server_fields(valid_ticket_payload):
    response = client.post("/tickets", json=valid_ticket_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["customer_email"] == "customer@example.com"
    assert body["category"] == "other"
    assert body["priority"] == "medium"
    assert body["status"] == "new"
    assert body["created_at"]
    assert body["updated_at"]


def test_create_ticket_rejects_invalid_payload(valid_ticket_payload):
    payload = valid_ticket_payload(customer_email="bad-email", description="short")

    response = client.post("/tickets", json=payload)

    assert response.status_code == 422
    assert "detail" in response.json()


def test_list_tickets_returns_created_tickets_in_order(valid_ticket_payload):
    first = client.post(
        "/tickets",
        json=valid_ticket_payload(customer_email="first@example.com"),
    ).json()
    second = client.post(
        "/tickets",
        json=valid_ticket_payload(customer_email="second@example.com"),
    ).json()

    response = client.get("/tickets")

    assert response.status_code == 200
    assert [ticket["id"] for ticket in response.json()] == [first["id"], second["id"]]


def test_list_tickets_filters_by_category_priority_and_status(valid_ticket_payload):
    matching = client.post(
        "/tickets",
        json=valid_ticket_payload(
            customer_email="billing@example.com",
            category="billing_question",
            priority="high",
            status="in_progress",
        ),
    ).json()
    client.post(
        "/tickets",
        json=valid_ticket_payload(
            customer_email="tech@example.com",
            category="technical_issue",
            priority="high",
            status="in_progress",
        ),
    )

    response = client.get(
        "/tickets?category=billing_question&priority=high&status=in_progress"
    )

    assert response.status_code == 200
    assert response.json() == [matching]


def test_get_ticket_returns_existing_ticket(valid_ticket_payload):
    created = client.post("/tickets", json=valid_ticket_payload()).json()

    response = client.get(f"/tickets/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_ticket_returns_404_for_missing_ticket():
    response = client.get("/tickets/missing-id")

    assert response.status_code == 404
    assert response.json() == {
        "error": "NotFound",
        "message": "ticket not found",
        "details": [],
    }


def test_update_ticket_changes_provided_fields(valid_ticket_payload):
    created = client.post("/tickets", json=valid_ticket_payload()).json()

    response = client.put(
        f"/tickets/{created['id']}",
        json={"status": "in_progress", "assigned_to": "agent-1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "in_progress"
    assert body["assigned_to"] == "agent-1"
    assert body["customer_email"] == "customer@example.com"


def test_update_ticket_rejects_invalid_fields(valid_ticket_payload):
    created = client.post("/tickets", json=valid_ticket_payload()).json()

    response = client.put(f"/tickets/{created['id']}", json={"priority": "soon"})

    assert response.status_code == 422


def test_update_ticket_returns_404_for_missing_ticket():
    response = client.put("/tickets/missing-id", json={"status": "closed"})

    assert response.status_code == 404
    assert response.json()["error"] == "NotFound"


def test_delete_ticket_returns_204_and_removes_ticket(valid_ticket_payload):
    created = client.post("/tickets", json=valid_ticket_payload()).json()

    response = client.delete(f"/tickets/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/tickets/{created['id']}").status_code == 404


def test_delete_ticket_returns_404_for_missing_ticket():
    response = client.delete("/tickets/missing-id")

    assert response.status_code == 404
    assert response.json()["error"] == "NotFound"


def test_auto_classify_ticket_returns_result_and_updates_ticket(valid_ticket_payload):
    created = client.post(
        "/tickets",
        json=valid_ticket_payload(
            subject="Critical password problem",
            description="I cannot access my login after changing my password.",
        ),
    ).json()

    response = client.post(f"/tickets/{created['id']}/auto-classify")

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "account_access"
    assert body["priority"] == "urgent"
    assert body["confidence"] > 0
    assert "password" in body["keywords_found"]

    stored = client.get(f"/tickets/{created['id']}").json()
    assert stored["category"] == "account_access"
    assert stored["priority"] == "urgent"
    assert stored["classification_confidence"] == body["confidence"]
    assert stored["classification_keywords"] == body["keywords_found"]
    assert stored["classification_overridden"] is False


def test_auto_classify_ticket_returns_404_for_missing_ticket():
    response = client.post("/tickets/missing-id/auto-classify")

    assert response.status_code == 404
    assert response.json()["error"] == "NotFound"


def test_import_tickets_from_json_returns_summary_and_created_tickets(valid_ticket_payload):
    payload = [
        valid_ticket_payload(customer_email="one@example.com"),
        valid_ticket_payload(customer_email="two@example.com"),
    ]

    response = client.post(
        "/tickets/import?format=json",
        files={"file": ("tickets.json", __import__("json").dumps(payload), "application/json")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["total_records"] == 2
    assert body["successful"] == 2
    assert body["failed"] == 0
    assert body["errors"] == []
    assert len(body["created_ticket_ids"]) == 2
    assert len(client.get("/tickets").json()) == 2


def test_import_tickets_reports_validation_failures_without_rejecting_valid_rows(valid_ticket_payload):
    payload = [
        valid_ticket_payload(customer_email="valid@example.com"),
        valid_ticket_payload(customer_email="bad-email", description="short"),
    ]

    response = client.post(
        "/tickets/import?format=json",
        files={"file": ("tickets.json", __import__("json").dumps(payload), "application/json")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["total_records"] == 2
    assert body["successful"] == 1
    assert body["failed"] == 1
    assert body["errors"][0]["record_number"] == 2
    assert "customer_email" in body["errors"][0]["message"]
    assert len(client.get("/tickets").json()) == 1


def test_import_tickets_rejects_malformed_file():
    response = client.post(
        "/tickets/import?format=json",
        files={"file": ("tickets.json", '{"tickets": [', "application/json")},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "ImportParseError"


def test_import_tickets_rejects_unsupported_format():
    response = client.post(
        "/tickets/import?format=xlsx",
        files={"file": ("tickets.xlsx", "not supported", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "ImportParseError"


def test_import_tickets_can_auto_classify_created_tickets(valid_ticket_payload):
    payload = [
        valid_ticket_payload(
            subject="Critical password issue",
            description="I cannot access my login after changing my password.",
        )
    ]

    response = client.post(
        "/tickets/import?format=json&auto_classify=true",
        files={"file": ("tickets.json", __import__("json").dumps(payload), "application/json")},
    )

    assert response.status_code == 201
    ticket = client.get(f"/tickets/{response.json()['created_ticket_ids'][0]}").json()
    assert ticket["category"] == "account_access"
    assert ticket["priority"] == "urgent"
    assert ticket["classification_confidence"] is not None
