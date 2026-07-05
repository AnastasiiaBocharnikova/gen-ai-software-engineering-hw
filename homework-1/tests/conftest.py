import pytest
from fastapi.testclient import TestClient

from banking_api.main import app, reset_store_for_tests


@pytest.fixture()
def client():
    reset_store_for_tests()
    return TestClient(app)


@pytest.fixture()
def auth_headers():
    return {"X-API-Key": "homework-api-key"}


@pytest.fixture()
def transfer_payload():
    return {
        "fromAccount": "ACC-12345",
        "toAccount": "ACC-67890",
        "amount": 100.50,
        "currency": "USD",
        "type": "transfer",
    }


@pytest.fixture()
def deposit_payload():
    return {
        "fromAccount": None,
        "toAccount": "ACC-12345",
        "amount": 250.00,
        "currency": "USD",
        "type": "deposit",
    }


@pytest.fixture()
def withdrawal_payload():
    return {
        "fromAccount": "ACC-12345",
        "toAccount": None,
        "amount": 75.25,
        "currency": "USD",
        "type": "withdrawal",
    }
