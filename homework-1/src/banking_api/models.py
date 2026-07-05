from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, field_serializer


def decimal_to_number(value: Decimal) -> Union[int, float]:
    if value == value.to_integral_value():
        return int(value)
    return float(value)


class TransactionType(str, Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    transfer = "transfer"


class TransactionStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class ApiModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class TransactionCreate(ApiModel):
    fromAccount: Optional[str] = None
    toAccount: Optional[str] = None
    amount: Decimal
    currency: str
    type: TransactionType


class Transaction(ApiModel):
    id: str
    fromAccount: Optional[str] = None
    toAccount: Optional[str] = None
    amount: Decimal
    currency: str
    type: TransactionType
    timestamp: datetime
    status: TransactionStatus

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal) -> Union[int, float]:
        return decimal_to_number(value)


class AccountBalance(ApiModel):
    accountId: str
    balance: Decimal
    currency: str

    @field_serializer("balance")
    def serialize_balance(self, value: Decimal) -> Union[int, float]:
        return decimal_to_number(value)


class AccountSummary(ApiModel):
    accountId: str
    totalDeposits: Decimal
    totalWithdrawals: Decimal
    transactionCount: int
    mostRecentTransactionDate: Optional[datetime]

    @field_serializer("totalDeposits", "totalWithdrawals")
    def serialize_money_totals(self, value: Decimal) -> Union[int, float]:
        return decimal_to_number(value)
