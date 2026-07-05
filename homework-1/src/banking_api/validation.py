from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from banking_api.models import TransactionCreate

VALID_CURRENCIES = {"USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "UAH"}
ACCOUNT_PATTERN = re.compile(r"^ACC-[A-Z0-9]{5}$")
CENT = Decimal("0.01")


class BusinessValidationError(ValueError):
    def __init__(self, details: list[dict[str, str]]) -> None:
        super().__init__("Validation failed")
        self.details = details


def validation_response(details: list[dict[str, str]]) -> dict[str, object]:
    return {"error": "Validation failed", "details": details}


def validate_transaction_payload(payload: TransactionCreate) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    amount = payload.amount
    currency = payload.currency.upper()
    transaction_type = payload.type.value if hasattr(payload.type, "value") else str(payload.type)

    if not _is_valid_decimal(amount) or amount <= 0:
        errors.append({"field": "amount", "message": "Amount must be a positive number"})
    elif amount.quantize(CENT) != amount:
        errors.append({"field": "amount", "message": "Amount must have at most 2 decimal places"})

    for field_name in ("fromAccount", "toAccount"):
        account = getattr(payload, field_name)
        if account is not None and not ACCOUNT_PATTERN.fullmatch(account):
            errors.append({"field": field_name, "message": "Account number must match ACC-XXXXX"})

    if currency not in VALID_CURRENCIES:
        errors.append({"field": "currency", "message": "Invalid currency code"})

    if transaction_type == "deposit":
        if payload.fromAccount is not None:
            errors.append({"field": "fromAccount", "message": "Deposit must not include fromAccount"})
        if not payload.toAccount:
            errors.append({"field": "toAccount", "message": "Deposit requires toAccount"})
    elif transaction_type == "withdrawal":
        if not payload.fromAccount:
            errors.append({"field": "fromAccount", "message": "Withdrawal requires fromAccount"})
        if payload.toAccount is not None:
            errors.append({"field": "toAccount", "message": "Withdrawal must not include toAccount"})
    elif transaction_type == "transfer":
        if not payload.fromAccount:
            errors.append({"field": "fromAccount", "message": "Transfer requires fromAccount"})
        if not payload.toAccount:
            errors.append({"field": "toAccount", "message": "Transfer requires toAccount"})
        if payload.fromAccount and payload.toAccount and payload.fromAccount == payload.toAccount:
            errors.append(
                {"field": "toAccount", "message": "Transfer destination must be different from source account"}
            )

    return errors


def _is_valid_decimal(amount: Decimal) -> bool:
    try:
        return amount.is_finite()
    except (AttributeError, InvalidOperation):
        return False
