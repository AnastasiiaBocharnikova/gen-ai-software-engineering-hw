import json
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from support_tickets.main import app, ticket_store


client = TestClient(app)


def setup_function():
    ticket_store.reset()


def valid_ticket_payload(index=0, **overrides):
    payload = {
        "customer_id": f"cust-perf-{index}",
        "customer_email": f"perf{index:03d}@example.com",
        "customer_name": f"Performance User {index}",
        "subject": "Cannot access account",
        "description": "I cannot access my account after changing my password.",
        "metadata": {
            "source": "api",
            "browser": "Chrome",
            "device_type": "desktop",
        },
        "tags": ["performance"],
    }
    payload.update(overrides)
    return payload


def test_creating_100_tickets_completes_quickly():
    start = time.perf_counter()

    for index in range(100):
        response = client.post("/tickets", json=valid_ticket_payload(index))
        assert response.status_code == 201

    elapsed = time.perf_counter() - start
    assert len(client.get("/tickets").json()) == 100
    assert elapsed < 3


def test_bulk_import_100_json_tickets_completes_quickly():
    payload = [valid_ticket_payload(index) for index in range(100)]
    start = time.perf_counter()

    response = client.post(
        "/tickets/import?format=json",
        files={"file": ("tickets.json", json.dumps(payload), "application/json")},
    )

    elapsed = time.perf_counter() - start
    assert response.status_code == 201
    assert response.json()["successful"] == 100
    assert elapsed < 2


def test_concurrent_creation_handles_20_simultaneous_requests():
    def create_ticket(index):
        return client.post("/tickets", json=valid_ticket_payload(index))

    with ThreadPoolExecutor(max_workers=20) as executor:
        responses = list(executor.map(create_ticket, range(20)))

    assert all(response.status_code == 201 for response in responses)
    assert len(client.get("/tickets").json()) == 20


def test_filtering_200_tickets_completes_quickly():
    for index in range(200):
        client.post(
            "/tickets",
            json=valid_ticket_payload(
                index,
                category="billing_question" if index % 2 == 0 else "technical_issue",
                priority="high" if index % 4 == 0 else "medium",
            ),
        )

    start = time.perf_counter()
    response = client.get("/tickets?category=billing_question&priority=high")
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert len(response.json()) == 50
    assert elapsed < 1


def test_auto_classifying_50_tickets_completes_quickly():
    ticket_ids = [
        client.post("/tickets", json=valid_ticket_payload(index)).json()["id"]
        for index in range(50)
    ]
    start = time.perf_counter()

    for ticket_id in ticket_ids:
        response = client.post(f"/tickets/{ticket_id}/auto-classify")
        assert response.status_code == 200

    elapsed = time.perf_counter() - start
    assert elapsed < 2
