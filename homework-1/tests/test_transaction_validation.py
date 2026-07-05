import pytest

from banking_api.models import TransactionCreate
from banking_api.validation import validate_transaction_payload


def make_payload(**overrides):
    data = {
        "fromAccount": "ACC-12345",
        "toAccount": "ACC-67890",
        "amount": 100.50,
        "currency": "USD",
        "type": "transfer",
    }
    data.update(overrides)
    return TransactionCreate(**data)


@pytest.mark.parametrize("amount", [0, -0.01, -100])
def test_validate_transaction_rejects_non_positive_amounts(amount):
    errors = validate_transaction_payload(make_payload(amount=amount))

    assert {"field": "amount", "message": "Amount must be a positive number"} in errors


@pytest.mark.parametrize("amount", [0.01, 1, 100.5, 999999.99])
def test_validate_transaction_accepts_positive_amounts_with_two_decimal_places(amount):
    errors = validate_transaction_payload(make_payload(amount=amount))

    assert errors == []


@pytest.mark.parametrize("amount", [0.001, 1.234, 100.999])
def test_validate_transaction_rejects_amounts_with_more_than_two_decimal_places(amount):
    errors = validate_transaction_payload(make_payload(amount=amount))

    assert errors == [{"field": "amount", "message": "Amount must have at most 2 decimal places"}]


@pytest.mark.parametrize("account", ["ACC-12345", "ACC-ABCDE", "ACC-A1B2C"])
def test_validate_transaction_accepts_valid_account_numbers(account):
    errors = validate_transaction_payload(make_payload(fromAccount=account))

    assert errors == []


@pytest.mark.parametrize("account", ["ACC-1234", "ACC-123456", "12345", "ACC_12345", "acc-12345"])
def test_validate_transaction_rejects_invalid_account_numbers(account):
    errors = validate_transaction_payload(make_payload(fromAccount=account))

    assert errors == [{"field": "fromAccount", "message": "Account number must match ACC-XXXXX"}]


@pytest.mark.parametrize("currency", ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "UAH"])
def test_validate_transaction_accepts_supported_iso_currency_codes(currency):
    errors = validate_transaction_payload(make_payload(currency=currency))

    assert errors == []


@pytest.mark.parametrize("currency", ["BTC", "US", "USDD", "123", ""])
def test_validate_transaction_rejects_unsupported_currency_codes(currency):
    errors = validate_transaction_payload(make_payload(currency=currency))

    assert errors == [{"field": "currency", "message": "Invalid currency code"}]


def test_validate_transaction_requires_to_account_for_deposit():
    errors = validate_transaction_payload(make_payload(type="deposit", fromAccount=None, toAccount=None))

    assert errors == [{"field": "toAccount", "message": "Deposit requires toAccount"}]


def test_validate_transaction_requires_from_account_for_withdrawal():
    errors = validate_transaction_payload(make_payload(type="withdrawal", fromAccount=None, toAccount=None))

    assert errors == [{"field": "fromAccount", "message": "Withdrawal requires fromAccount"}]


def test_validate_transaction_requires_both_accounts_for_transfer():
    errors = validate_transaction_payload(make_payload(fromAccount=None, toAccount=None))

    assert errors == [
        {"field": "fromAccount", "message": "Transfer requires fromAccount"},
        {"field": "toAccount", "message": "Transfer requires toAccount"},
    ]
