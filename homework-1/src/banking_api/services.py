from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional, Union
from uuid import uuid4

from banking_api.models import AccountBalance, AccountSummary, Transaction, TransactionCreate, TransactionType
from banking_api.store import TransactionStore
from banking_api.validation import BusinessValidationError, validate_transaction_payload

ZERO = Decimal("0.00")


def create_transaction(payload: TransactionCreate, store: TransactionStore) -> Transaction:
    normalized = TransactionCreate(
        fromAccount=payload.fromAccount,
        toAccount=payload.toAccount,
        amount=payload.amount,
        currency=payload.currency.upper(),
        type=payload.type,
    )
    errors = validate_transaction_payload(normalized)
    if errors:
        raise BusinessValidationError(errors)

    balance = calculate_balance(normalized.fromAccount, store.list()).balance if normalized.fromAccount else ZERO
    if normalized.type in {TransactionType.withdrawal, TransactionType.transfer, "withdrawal", "transfer"}:
        if normalized.amount > balance:
            raise BusinessValidationError([{"field": "amount", "message": "Insufficient funds"}])

    transaction = Transaction(
        id=str(uuid4()),
        fromAccount=normalized.fromAccount,
        toAccount=normalized.toAccount,
        amount=normalized.amount.quantize(Decimal("0.01")),
        currency=normalized.currency,
        type=normalized.type,
        timestamp=datetime.now(timezone.utc),
        status="completed",
    )
    return store.add(transaction)


def calculate_balance(account_id: Optional[str], transactions: list[Transaction]) -> AccountBalance:
    if not account_id:
        return AccountBalance(accountId="", balance=ZERO, currency="USD")

    matching = [tx for tx in transactions if tx.fromAccount == account_id or tx.toAccount == account_id]
    currency = matching[-1].currency if matching else "USD"
    balance = ZERO

    for tx in matching:
        if tx.type == TransactionType.deposit or tx.type == "deposit":
            if tx.toAccount == account_id:
                balance += tx.amount
        elif tx.type == TransactionType.withdrawal or tx.type == "withdrawal":
            if tx.fromAccount == account_id:
                balance -= tx.amount
        elif tx.type == TransactionType.transfer or tx.type == "transfer":
            if tx.fromAccount == account_id:
                balance -= tx.amount
            if tx.toAccount == account_id:
                balance += tx.amount

    return AccountBalance(accountId=account_id, balance=balance.quantize(Decimal("0.01")), currency=currency)


def filter_transactions(
    transactions: list[Transaction],
    account_id: Optional[str] = None,
    transaction_type: Optional[Union[TransactionType, str]] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> list[Transaction]:
    if from_date and to_date and from_date > to_date:
        raise BusinessValidationError(
            [{"field": "dateRange", "message": "from date must be before or equal to to date"}]
        )

    filtered = transactions
    requested_type = transaction_type.value if hasattr(transaction_type, "value") else transaction_type

    if account_id:
        filtered = [tx for tx in filtered if tx.fromAccount == account_id or tx.toAccount == account_id]
    if requested_type:
        filtered = [tx for tx in filtered if tx.type == requested_type]
    if from_date:
        filtered = [tx for tx in filtered if tx.timestamp.date() >= from_date]
    if to_date:
        filtered = [tx for tx in filtered if tx.timestamp.date() <= to_date]

    return filtered


def calculate_account_summary(account_id: str, transactions: list[Transaction]) -> AccountSummary:
    matching = [tx for tx in transactions if tx.fromAccount == account_id or tx.toAccount == account_id]
    total_deposits = ZERO
    total_withdrawals = ZERO

    for tx in matching:
        if (tx.type == TransactionType.deposit or tx.type == "deposit") and tx.toAccount == account_id:
            total_deposits += tx.amount
        elif (tx.type == TransactionType.withdrawal or tx.type == "withdrawal") and tx.fromAccount == account_id:
            total_withdrawals += tx.amount
        elif (tx.type == TransactionType.transfer or tx.type == "transfer") and tx.fromAccount == account_id:
            total_withdrawals += tx.amount

    return AccountSummary(
        accountId=account_id,
        totalDeposits=total_deposits.quantize(Decimal("0.01")),
        totalWithdrawals=total_withdrawals.quantize(Decimal("0.01")),
        transactionCount=len(matching),
        mostRecentTransactionDate=max((tx.timestamp for tx in matching), default=None),
    )
