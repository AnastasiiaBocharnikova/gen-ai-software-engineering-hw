import json

from fastapi.testclient import TestClient

from support_tickets.main import app, ticket_store


client = TestClient(app)


def setup_function():
    ticket_store.reset()


def test_create_ticket_rejects_missing_required_fields():
    response = client.post(
        "/tickets",
        json={
            "customer_id": "missing-fields",
            "customer_email": "missing@example.com",
        },
    )

    assert response.status_code == 422
    fields = {error["loc"][-1] for error in response.json()["detail"]}
    assert {"customer_name", "subject", "description", "metadata"}.issubset(fields)


def test_create_ticket_rejects_invalid_enum_values(valid_ticket_payload):
    response = client.post(
        "/tickets",
        json=valid_ticket_payload(
            category="security_problem",
            priority="immediate",
            status="started",
            metadata={
                "source": "fax",
                "browser": "Chrome",
                "device_type": "watch",
            },
        ),
    )

    assert response.status_code == 422
    message = json.dumps(response.json())
    assert "category" in message
    assert "priority" in message
    assert "status" in message
    assert "source" in message
    assert "device_type" in message


def test_list_tickets_rejects_invalid_filter_values():
    response = client.get("/tickets?category=wrong&priority=now&status=unknown")

    assert response.status_code == 422
    message = json.dumps(response.json())
    assert "category" in message
    assert "priority" in message
    assert "status" in message


def test_update_ticket_rejects_short_description_and_invalid_email(valid_ticket_payload):
    created = client.post("/tickets", json=valid_ticket_payload()).json()

    response = client.put(
        f"/tickets/{created['id']}",
        json={
            "customer_email": "invalid-email",
            "description": "short",
        },
    )

    assert response.status_code == 422
    message = json.dumps(response.json())
    assert "customer_email" in message
    assert "description" in message


def test_import_rejects_missing_upload_file():
    response = client.post("/tickets/import?format=json")

    assert response.status_code == 422
    assert "file" in json.dumps(response.json())


def test_import_csv_with_invalid_record_returns_failed_summary():
    content = (
        "customer_id,customer_email,customer_name,subject,description,"
        "metadata_source,metadata_browser,metadata_device_type\n"
        "bad-1,not-an-email,Bad User,Bad ticket,short,web_form,Chrome,desktop\n"
    )

    response = client.post(
        "/tickets/import?format=csv",
        files={"file": ("invalid_tickets.csv", content, "text/csv")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["total_records"] == 1
    assert body["successful"] == 0
    assert body["failed"] == 1
    assert "customer_email" in body["errors"][0]["message"]
    assert client.get("/tickets").json() == []
