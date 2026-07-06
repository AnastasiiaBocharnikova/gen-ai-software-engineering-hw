# Homework 1 Banking API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python REST API for banking transactions that satisfies Homework 1 Tasks 1-4.

**Architecture:** Use FastAPI with an in-memory transaction repository. Keep validation, balance calculations, filtering, and summary logic in focused modules so each requirement can be tested directly without running a real server.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic, pytest, httpx/TestClient, Uvicorn.

---

## File Structure

- Create: `homework-1/requirements.txt` - runtime and test dependencies.
- Create: `homework-1/.gitignore` - Python cache, virtualenv, and local env exclusions.
- Create: `homework-1/src/banking_api/__init__.py` - package marker.
- Create: `homework-1/src/banking_api/models.py` - enums, Pydantic request/response models, validation error shape.
- Create: `homework-1/src/banking_api/validation.py` - reusable transaction validation rules from Task 2.
- Create: `homework-1/src/banking_api/store.py` - in-memory transaction storage and lookup.
- Create: `homework-1/src/banking_api/services.py` - create transaction, filter history, balance, and account summary logic.
- Create: `homework-1/src/banking_api/main.py` - FastAPI app and route definitions.
- Create: `homework-1/tests/__init__.py` - package marker for tests.
- Create: `homework-1/tests/conftest.py` - isolated FastAPI test client fixture.
- Create: `homework-1/tests/test_transactions_api.py` - endpoint tests for Tasks 1-4.
- Create: `homework-1/demo/run.sh` - script to run the API.
- Create: `homework-1/demo/sample-requests.sh` - curl examples.
- Create: `homework-1/demo/sample-data.json` - sample transaction payloads.
- Modify: `homework-1/README.md` - overview, features, AI usage, architecture.
- Modify: `homework-1/HOWTORUN.md` - setup, run, and test commands.

## Task 1: Core API Implementation

**Files:**
- Create: `homework-1/requirements.txt`
- Create: `homework-1/src/banking_api/__init__.py`
- Create: `homework-1/src/banking_api/models.py`
- Create: `homework-1/src/banking_api/store.py`
- Create: `homework-1/src/banking_api/services.py`
- Create: `homework-1/src/banking_api/main.py`
- Create: `homework-1/tests/conftest.py`
- Create: `homework-1/tests/test_transactions_api.py`

- [ ] **Step 1: Add Python dependencies**

Write `homework-1/requirements.txt`:

```text
fastapi==0.115.6
uvicorn[standard]==0.34.0
pytest==8.3.4
httpx==0.28.1
```

- [ ] **Step 2: Write failing tests for core endpoints**

Create `homework-1/tests/conftest.py`:

```python
import pytest
from fastapi.testclient import TestClient

from banking_api.main import app, reset_store_for_tests


@pytest.fixture()
def client():
    reset_store_for_tests()
    return TestClient(app)
```

Create `homework-1/tests/test_transactions_api.py` with these initial tests:

```python
def valid_transfer_payload():
    return {
        "fromAccount": "ACC-12345",
        "toAccount": "ACC-67890",
        "amount": 100.50,
        "currency": "USD",
        "type": "transfer",
    }


def test_create_transaction_returns_created_transaction(client):
    response = client.post("/transactions", json=valid_transfer_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["fromAccount"] == "ACC-12345"
    assert body["toAccount"] == "ACC-67890"
    assert body["amount"] == 100.50
    assert body["currency"] == "USD"
    assert body["type"] == "transfer"
    assert body["status"] == "completed"
    assert body["timestamp"]


def test_list_transactions_returns_created_transactions(client):
    created = client.post("/transactions", json=valid_transfer_payload()).json()

    response = client.get("/transactions")

    assert response.status_code == 200
    assert response.json() == [created]


def test_get_transaction_by_id(client):
    created = client.post("/transactions", json=valid_transfer_payload()).json()

    response = client.get(f"/transactions/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_missing_transaction_returns_404(client):
    response = client.get("/transactions/missing-id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Transaction not found"}


def test_account_balance_includes_incoming_and_outgoing_transfers(client):
    client.post("/transactions", json=valid_transfer_payload())

    from_balance = client.get("/accounts/ACC-12345/balance")
    to_balance = client.get("/accounts/ACC-67890/balance")

    assert from_balance.status_code == 200
    assert from_balance.json() == {"accountId": "ACC-12345", "balance": -100.50, "currency": "USD"}
    assert to_balance.status_code == 200
    assert to_balance.json() == {"accountId": "ACC-67890", "balance": 100.50, "currency": "USD"}
```

- [ ] **Step 3: Run tests and verify they fail because the package does not exist**

Run:

```bash
cd homework-1
PYTHONPATH=src pytest -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'banking_api'`.

- [ ] **Step 4: Implement models, store, services, and routes**

Create `homework-1/src/banking_api/models.py`:

```python
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict


class TransactionType(str, Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    transfer = "transfer"


class TransactionStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class TransactionCreate(BaseModel):
    fromAccount: str | None = None
    toAccount: str | None = None
    amount: float
    currency: str
    type: TransactionType


class Transaction(BaseModel):
    id: str
    fromAccount: str | None = None
    toAccount: str | None = None
    amount: float
    currency: str
    type: TransactionType
    timestamp: datetime
    status: TransactionStatus

    model_config = ConfigDict(use_enum_values=True)


class AccountBalance(BaseModel):
    accountId: str
    balance: float
    currency: str
```

Create `homework-1/src/banking_api/store.py`:

```python
from banking_api.models import Transaction


class TransactionStore:
    def __init__(self):
        self._transactions: dict[str, Transaction] = {}

    def add(self, transaction: Transaction) -> Transaction:
        self._transactions[transaction.id] = transaction
        return transaction

    def list(self) -> list[Transaction]:
        return list(self._transactions.values())

    def get(self, transaction_id: str) -> Transaction | None:
        return self._transactions.get(transaction_id)

    def clear(self) -> None:
        self._transactions.clear()
```

Create `homework-1/src/banking_api/services.py`:

```python
from datetime import datetime, timezone
from uuid import uuid4

from banking_api.models import AccountBalance, Transaction, TransactionCreate
from banking_api.store import TransactionStore


def create_transaction(payload: TransactionCreate, store: TransactionStore) -> Transaction:
    transaction = Transaction(
        id=str(uuid4()),
        fromAccount=payload.fromAccount,
        toAccount=payload.toAccount,
        amount=payload.amount,
        currency=payload.currency.upper(),
        type=payload.type,
        timestamp=datetime.now(timezone.utc),
        status="completed",
    )
    return store.add(transaction)


def calculate_balance(account_id: str, transactions: list[Transaction]) -> AccountBalance:
    matching = [tx for tx in transactions if tx.fromAccount == account_id or tx.toAccount == account_id]
    currency = matching[-1].currency if matching else "USD"
    balance = 0.0

    for tx in matching:
        if tx.type == "deposit" and tx.toAccount == account_id:
            balance += tx.amount
        elif tx.type == "withdrawal" and tx.fromAccount == account_id:
            balance -= tx.amount
        elif tx.type == "transfer":
            if tx.fromAccount == account_id:
                balance -= tx.amount
            if tx.toAccount == account_id:
                balance += tx.amount

    return AccountBalance(accountId=account_id, balance=round(balance, 2), currency=currency)
```

Create `homework-1/src/banking_api/main.py`:

```python
from fastapi import FastAPI, HTTPException

from banking_api.models import AccountBalance, Transaction, TransactionCreate
from banking_api.services import calculate_balance, create_transaction
from banking_api.store import TransactionStore

app = FastAPI(title="Banking Transactions API")
store = TransactionStore()


def reset_store_for_tests() -> None:
    store.clear()


@app.post("/transactions", response_model=Transaction, status_code=201)
def post_transaction(payload: TransactionCreate) -> Transaction:
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be a positive number")
    return create_transaction(payload, store)


@app.get("/transactions", response_model=list[Transaction])
def get_transactions() -> list[Transaction]:
    return store.list()


@app.get("/transactions/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: str) -> Transaction:
    transaction = store.get(transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.get("/accounts/{account_id}/balance", response_model=AccountBalance)
def get_account_balance(account_id: str) -> AccountBalance:
    return calculate_balance(account_id, store.list())
```

- [ ] **Step 5: Run Task 1 tests and verify they pass**

Run:

```bash
cd homework-1
PYTHONPATH=src pytest -q
```

Expected: PASS for the Task 1 tests.

- [ ] **Step 6: Commit Task 1**

```bash
git add homework-1
git commit -m "feat: implement core banking transactions API"
```

## Task 2: Transaction Validation

**Files:**
- Create: `homework-1/src/banking_api/validation.py`
- Modify: `homework-1/src/banking_api/models.py`
- Modify: `homework-1/src/banking_api/main.py`
- Modify: `homework-1/tests/test_transactions_api.py`

- [ ] **Step 1: Add failing validation tests**

Append to `homework-1/tests/test_transactions_api.py`:

```python
def test_create_transaction_rejects_invalid_payload_with_details(client):
    payload = {
        "fromAccount": "BAD",
        "toAccount": "ACC-67890",
        "amount": -10,
        "currency": "XYZ",
        "type": "transfer",
    }

    response = client.post("/transactions", json=payload)

    assert response.status_code == 400
    assert response.json() == {
        "error": "Validation failed",
        "details": [
            {"field": "amount", "message": "Amount must be a positive number"},
            {"field": "fromAccount", "message": "Account number must match ACC-XXXXX"},
            {"field": "currency", "message": "Invalid currency code"},
        ],
    }


def test_create_transaction_rejects_more_than_two_decimal_places(client):
    payload = valid_transfer_payload()
    payload["amount"] = 10.123

    response = client.post("/transactions", json=payload)

    assert response.status_code == 400
    assert response.json()["details"] == [
        {"field": "amount", "message": "Amount must have at most 2 decimal places"}
    ]


def test_deposit_requires_to_account(client):
    payload = {
        "amount": 25,
        "currency": "EUR",
        "type": "deposit",
        "fromAccount": None,
        "toAccount": None,
    }

    response = client.post("/transactions", json=payload)

    assert response.status_code == 400
    assert response.json()["details"] == [
        {"field": "toAccount", "message": "Deposit requires toAccount"}
    ]


def test_withdrawal_requires_from_account(client):
    payload = {
        "amount": 25,
        "currency": "GBP",
        "type": "withdrawal",
        "fromAccount": None,
        "toAccount": None,
    }

    response = client.post("/transactions", json=payload)

    assert response.status_code == 400
    assert response.json()["details"] == [
        {"field": "fromAccount", "message": "Withdrawal requires fromAccount"}
    ]
```

- [ ] **Step 2: Run validation tests and verify they fail**

Run:

```bash
cd homework-1
PYTHONPATH=src pytest tests/test_transactions_api.py -q
```

Expected: FAIL because validation returns FastAPI defaults or incomplete messages.

- [ ] **Step 3: Implement validation helpers**

Create `homework-1/src/banking_api/validation.py`:

```python
import re
from decimal import Decimal, InvalidOperation
from typing import Any

VALID_CURRENCIES = {"USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "UAH"}
ACCOUNT_PATTERN = re.compile(r"^ACC-[A-Za-z0-9]{5}$")


def validate_transaction_payload(payload: Any) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    amount = payload.amount
    currency = payload.currency.upper()
    transaction_type = payload.type.value if hasattr(payload.type, "value") else payload.type

    if amount <= 0:
        errors.append({"field": "amount", "message": "Amount must be a positive number"})
    elif _has_more_than_two_decimal_places(amount):
        errors.append({"field": "amount", "message": "Amount must have at most 2 decimal places"})

    for field_name in ("fromAccount", "toAccount"):
        account = getattr(payload, field_name)
        if account is not None and not ACCOUNT_PATTERN.match(account):
            errors.append({"field": field_name, "message": "Account number must match ACC-XXXXX"})

    if currency not in VALID_CURRENCIES:
        errors.append({"field": "currency", "message": "Invalid currency code"})

    if transaction_type == "deposit" and not payload.toAccount:
        errors.append({"field": "toAccount", "message": "Deposit requires toAccount"})
    if transaction_type == "withdrawal" and not payload.fromAccount:
        errors.append({"field": "fromAccount", "message": "Withdrawal requires fromAccount"})
    if transaction_type == "transfer":
        if not payload.fromAccount:
            errors.append({"field": "fromAccount", "message": "Transfer requires fromAccount"})
        if not payload.toAccount:
            errors.append({"field": "toAccount", "message": "Transfer requires toAccount"})

    return errors


def _has_more_than_two_decimal_places(amount: float) -> bool:
    try:
        decimal_amount = Decimal(str(amount))
    except InvalidOperation:
        return True
    return decimal_amount.as_tuple().exponent < -2
```

- [ ] **Step 4: Use validation in route**

Update `homework-1/src/banking_api/main.py` so `post_transaction` becomes:

```python
from fastapi.responses import JSONResponse
from banking_api.validation import validate_transaction_payload


@app.post("/transactions", response_model=Transaction, status_code=201)
def post_transaction(payload: TransactionCreate) -> Transaction | JSONResponse:
    errors = validate_transaction_payload(payload)
    if errors:
        return JSONResponse(status_code=400, content={"error": "Validation failed", "details": errors})
    return create_transaction(payload, store)
```

- [ ] **Step 5: Run all tests and verify validation passes**

Run:

```bash
cd homework-1
PYTHONPATH=src pytest -q
```

Expected: PASS.

- [ ] **Step 6: Commit Task 2**

```bash
git add homework-1
git commit -m "feat: add transaction validation"
```

## Task 3: Basic Transaction History Filtering

**Files:**
- Modify: `homework-1/src/banking_api/services.py`
- Modify: `homework-1/src/banking_api/main.py`
- Modify: `homework-1/tests/test_transactions_api.py`

- [ ] **Step 1: Add failing filter tests**

Append to `homework-1/tests/test_transactions_api.py`:

```python
def create_transaction(client, payload):
    return client.post("/transactions", json=payload).json()


def test_filter_transactions_by_account(client):
    create_transaction(client, valid_transfer_payload())
    create_transaction(client, {
        "fromAccount": "ACC-11111",
        "toAccount": "ACC-22222",
        "amount": 20,
        "currency": "USD",
        "type": "transfer",
    })

    response = client.get("/transactions?accountId=ACC-12345")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["fromAccount"] == "ACC-12345"


def test_filter_transactions_by_type(client):
    create_transaction(client, valid_transfer_payload())
    create_transaction(client, {
        "fromAccount": None,
        "toAccount": "ACC-12345",
        "amount": 40,
        "currency": "USD",
        "type": "deposit",
    })

    response = client.get("/transactions?type=deposit")

    assert response.status_code == 200
    assert [tx["type"] for tx in response.json()] == ["deposit"]


def test_filter_transactions_by_date_range(client):
    create_transaction(client, valid_transfer_payload())

    response = client.get("/transactions?from=2020-01-01&to=2099-01-31")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_transactions_combines_filters(client):
    create_transaction(client, valid_transfer_payload())
    create_transaction(client, {
        "fromAccount": None,
        "toAccount": "ACC-12345",
        "amount": 40,
        "currency": "USD",
        "type": "deposit",
    })

    response = client.get("/transactions?accountId=ACC-12345&type=transfer&from=2020-01-01&to=2099-01-31")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["type"] == "transfer"
```

- [ ] **Step 2: Run filter tests and verify they fail**

Run:

```bash
cd homework-1
PYTHONPATH=src pytest tests/test_transactions_api.py::test_filter_transactions_by_account tests/test_transactions_api.py::test_filter_transactions_by_type tests/test_transactions_api.py::test_filter_transactions_by_date_range tests/test_transactions_api.py::test_filter_transactions_combines_filters -q
```

Expected: FAIL because `/transactions` ignores query parameters.

- [ ] **Step 3: Implement filtering service**

Add to `homework-1/src/banking_api/services.py`:

```python
from datetime import date
from banking_api.models import TransactionType


def filter_transactions(
    transactions: list[Transaction],
    account_id: str | None = None,
    transaction_type: TransactionType | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[Transaction]:
    filtered = transactions

    if account_id:
        filtered = [tx for tx in filtered if tx.fromAccount == account_id or tx.toAccount == account_id]
    if transaction_type:
        filtered = [tx for tx in filtered if tx.type == transaction_type]
    if from_date:
        filtered = [tx for tx in filtered if tx.timestamp.date() >= from_date]
    if to_date:
        filtered = [tx for tx in filtered if tx.timestamp.date() <= to_date]

    return filtered
```

- [ ] **Step 4: Wire filters into route**

Update `homework-1/src/banking_api/main.py` imports:

```python
from datetime import date
from fastapi import Query
from banking_api.models import AccountBalance, Transaction, TransactionCreate, TransactionType
from banking_api.services import calculate_balance, create_transaction, filter_transactions
```

Replace `get_transactions`:

```python
@app.get("/transactions", response_model=list[Transaction])
def get_transactions(
    account_id: str | None = Query(default=None, alias="accountId"),
    transaction_type: TransactionType | None = Query(default=None, alias="type"),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
) -> list[Transaction]:
    return filter_transactions(store.list(), account_id, transaction_type, from_date, to_date)
```

- [ ] **Step 5: Run all tests and verify filters pass**

Run:

```bash
cd homework-1
PYTHONPATH=src pytest -q
```

Expected: PASS.

- [ ] **Step 6: Commit Task 3**

```bash
git add homework-1
git commit -m "feat: add transaction history filters"
```

## Task 4: Additional Feature - Account Summary Endpoint

**Chosen option:** Option A, `GET /accounts/:accountId/summary`. It is the best fit for this project because it builds directly on the in-memory transactions and balance/history logic already created.

**Files:**
- Modify: `homework-1/src/banking_api/models.py`
- Modify: `homework-1/src/banking_api/services.py`
- Modify: `homework-1/src/banking_api/main.py`
- Modify: `homework-1/tests/test_transactions_api.py`

- [ ] **Step 1: Add failing summary endpoint test**

Append to `homework-1/tests/test_transactions_api.py`:

```python
def test_account_summary_returns_totals_count_and_recent_date(client):
    create_transaction(client, {
        "fromAccount": None,
        "toAccount": "ACC-12345",
        "amount": 150,
        "currency": "USD",
        "type": "deposit",
    })
    create_transaction(client, {
        "fromAccount": "ACC-12345",
        "toAccount": None,
        "amount": 25,
        "currency": "USD",
        "type": "withdrawal",
    })
    create_transaction(client, {
        "fromAccount": "ACC-12345",
        "toAccount": "ACC-67890",
        "amount": 10,
        "currency": "USD",
        "type": "transfer",
    })

    response = client.get("/accounts/ACC-12345/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["accountId"] == "ACC-12345"
    assert body["totalDeposits"] == 150
    assert body["totalWithdrawals"] == 35
    assert body["transactionCount"] == 3
    assert body["mostRecentTransactionDate"]
```

- [ ] **Step 2: Run summary test and verify it fails**

Run:

```bash
cd homework-1
PYTHONPATH=src pytest tests/test_transactions_api.py::test_account_summary_returns_totals_count_and_recent_date -q
```

Expected: FAIL with 404 because the summary route does not exist.

- [ ] **Step 3: Add summary model**

Add to `homework-1/src/banking_api/models.py`:

```python
class AccountSummary(BaseModel):
    accountId: str
    totalDeposits: float
    totalWithdrawals: float
    transactionCount: int
    mostRecentTransactionDate: datetime | None
```

- [ ] **Step 4: Add summary service**

Add to `homework-1/src/banking_api/services.py`:

```python
from banking_api.models import AccountSummary


def calculate_account_summary(account_id: str, transactions: list[Transaction]) -> AccountSummary:
    matching = [tx for tx in transactions if tx.fromAccount == account_id or tx.toAccount == account_id]
    total_deposits = 0.0
    total_withdrawals = 0.0

    for tx in matching:
        if tx.type == "deposit" and tx.toAccount == account_id:
            total_deposits += tx.amount
        elif tx.type == "withdrawal" and tx.fromAccount == account_id:
            total_withdrawals += tx.amount
        elif tx.type == "transfer" and tx.fromAccount == account_id:
            total_withdrawals += tx.amount

    most_recent = max((tx.timestamp for tx in matching), default=None)
    return AccountSummary(
        accountId=account_id,
        totalDeposits=round(total_deposits, 2),
        totalWithdrawals=round(total_withdrawals, 2),
        transactionCount=len(matching),
        mostRecentTransactionDate=most_recent,
    )
```

- [ ] **Step 5: Add summary route**

Update `homework-1/src/banking_api/main.py` imports:

```python
from banking_api.models import AccountBalance, AccountSummary, Transaction, TransactionCreate, TransactionType
from banking_api.services import calculate_account_summary, calculate_balance, create_transaction, filter_transactions
```

Add route:

```python
@app.get("/accounts/{account_id}/summary", response_model=AccountSummary)
def get_account_summary(account_id: str) -> AccountSummary:
    return calculate_account_summary(account_id, store.list())
```

- [ ] **Step 6: Run all tests and verify summary passes**

Run:

```bash
cd homework-1
PYTHONPATH=src pytest -q
```

Expected: PASS.

- [ ] **Step 7: Commit Task 4**

```bash
git add homework-1
git commit -m "feat: add account transaction summary"
```

## Documentation and Demo Task

**Files:**
- Create: `homework-1/.gitignore`
- Create: `homework-1/demo/run.sh`
- Create: `homework-1/demo/sample-requests.sh`
- Create: `homework-1/demo/sample-data.json`
- Modify: `homework-1/README.md`
- Modify: `homework-1/HOWTORUN.md`

- [ ] **Step 1: Add project `.gitignore`**

Create `homework-1/.gitignore`:

```text
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
htmlcov/
.venv/
venv/
.env
```

- [ ] **Step 2: Add run script**

Create `homework-1/demo/run.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
PYTHONPATH=src uvicorn banking_api.main:app --reload --host 127.0.0.1 --port 3000
```

Run:

```bash
chmod +x homework-1/demo/run.sh
```

- [ ] **Step 3: Add sample requests**

Create `homework-1/demo/sample-requests.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:3000}"

curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{"fromAccount":"ACC-12345","toAccount":"ACC-67890","amount":100.50,"currency":"USD","type":"transfer"}'

curl -s "$BASE_URL/transactions"
curl -s "$BASE_URL/transactions?accountId=ACC-12345&type=transfer"
curl -s "$BASE_URL/accounts/ACC-12345/balance"
curl -s "$BASE_URL/accounts/ACC-12345/summary"
```

Run:

```bash
chmod +x homework-1/demo/sample-requests.sh
```

- [ ] **Step 4: Add sample data**

Create `homework-1/demo/sample-data.json`:

```json
[
  {
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": 100.5,
    "currency": "USD",
    "type": "transfer"
  },
  {
    "fromAccount": null,
    "toAccount": "ACC-12345",
    "amount": 250,
    "currency": "USD",
    "type": "deposit"
  }
]
```

- [ ] **Step 5: Update documentation**

Update `homework-1/README.md` with:

```markdown
# Homework 1: Banking Transactions API

> **Student Name**: Anastasiia Bocarnikova
> **Date Submitted**: 2026-07-05
> **AI Tools Used**: Codex

## Project Overview

This project implements a Python/FastAPI REST API for banking transactions using in-memory storage.

## Features

- Create, list, and fetch transactions
- Account balance calculation
- Validation for amount, account format, currency, and transaction-specific accounts
- Transaction history filters by account, type, and date range
- Account summary endpoint with deposits, withdrawals, count, and most recent transaction date

## Architecture

- `models.py`: API request and response models
- `validation.py`: business validation rules
- `store.py`: in-memory transaction repository
- `services.py`: transaction, balance, filter, and summary logic
- `main.py`: FastAPI routes

## AI-Assisted Development Notes

Codex was used to plan the implementation, generate tests first, and then implement each homework task sequentially.
```

Update `homework-1/HOWTORUN.md` with:

````markdown
# How to Run the Application

## Setup

```bash
cd homework-1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run API

```bash
./demo/run.sh
```

The API runs at `http://127.0.0.1:3000`.

## Run Tests

```bash
PYTHONPATH=src pytest -q
```

## Try Sample Requests

In another terminal:

```bash
./demo/sample-requests.sh
```
````

- [ ] **Step 6: Run final verification**

Run:

```bash
cd homework-1
PYTHONPATH=src pytest -q
```

Expected: PASS.

- [ ] **Step 7: Commit documentation and demo files**

```bash
git add homework-1
git commit -m "docs: add banking api run instructions and demos"
```

## Final Manual Verification

- [ ] Start the API:

```bash
cd homework-1
./demo/run.sh
```

- [ ] In a second terminal, run sample requests:

```bash
cd homework-1
./demo/sample-requests.sh
```

Expected:
- `POST /transactions` returns `201` with an auto-generated `id`.
- `GET /transactions` returns stored transactions.
- `GET /transactions?accountId=ACC-12345&type=transfer` returns filtered results.
- `GET /accounts/ACC-12345/balance` returns a calculated balance.
- `GET /accounts/ACC-12345/summary` returns deposits, withdrawals, count, and recent transaction date.

## Self-Review

- Spec coverage: Task 1 core API, Task 2 validation, Task 3 filtering, and Task 4 Option A summary are all mapped to tasks above.
- Placeholder scan: The plan contains no unresolved placeholders, unspecified validations, or generic test steps.
- Type consistency: Routes use `TransactionCreate`, `Transaction`, `AccountBalance`, and `AccountSummary` consistently across models, services, tests, and FastAPI route signatures.
