from __future__ import annotations

from typing import Optional

from banking_api.models import Transaction


class TransactionStore:
    def __init__(self) -> None:
        self._transactions: dict[str, Transaction] = {}

    def add(self, transaction: Transaction) -> Transaction:
        self._transactions[transaction.id] = transaction
        return transaction

    def list(self) -> list[Transaction]:
        return list(self._transactions.values())

    def get(self, transaction_id: str) -> Optional[Transaction]:
        return self._transactions.get(transaction_id)

    def clear(self) -> None:
        self._transactions.clear()
