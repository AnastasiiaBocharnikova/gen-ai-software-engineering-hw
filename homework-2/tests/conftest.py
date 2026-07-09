import pytest


@pytest.fixture
def valid_ticket_payload():
    def build(**overrides):
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

    return build
