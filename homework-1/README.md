# Homework 1: Banking Transactions API

> **Student Name**: Anastasiia Bocharnikova  
> **Date Submitted**: 2026-07-05  
> **AI Tools Used**: Codex

## Project Overview

This project is a minimal banking transactions REST API built for the AI-Assisted Development course. It lets a client create banking transactions, list and filter transaction history, look up individual transactions, calculate account balances, and view account summaries.

The API is intentionally small and uses in-memory storage, but it includes practical validation and error-handling rules suitable for a homework banking API:

- money is handled with Python `Decimal` values internally
- invalid transactions return structured validation errors
- overdraft withdrawals and transfers are rejected
- read endpoints require a simple API key
- malformed request bodies return schema-level errors instead of crashing

## Architecture

The application is a FastAPI service with a simple layered structure:

- **Routes** in `main.py` expose HTTP endpoints and map errors to HTTP responses.
- **Models** in `models.py` define request and response shapes.
- **Validation** in `validation.py` checks business rules before transactions are stored.
- **Services** in `services.py` contain transaction creation, filtering, balance, and summary logic.
- **Store** in `store.py` keeps transactions in memory for the lifetime of the running process.

There is no database. Restarting the application clears all transactions.

## Technology Stack

- Python 3
- FastAPI `0.115.6`
- Uvicorn `0.34.0`
- Pydantic `2.x`, installed through FastAPI
- pytest `8.3.4`
- httpx `0.28.1`, used by FastAPI's test client

## Project Structure

```text
homework-1/
├── README.md
├── HOWTORUN.md
├── requirements.txt
├── .gitignore
├── demo/
│   ├── run.sh
│   ├── sample-data.json
│   └── sample-requests.sh
├── docs/
│   └── screenshots/
├── src/
│   └── banking_api/
│       ├── __init__.py
│       ├── main.py
│       ├── models.py
│       ├── services.py
│       ├── store.py
│       └── validation.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_transaction_api.py
    ├── test_transaction_services.py
    └── test_transaction_validation.py
```

## Setup and Installation

From the repository root:

```bash
cd homework-1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the Application Locally

Start the API:

```bash
cd homework-1
./demo/run.sh
```

The service runs at:

```text
http://127.0.0.1:3000
```

FastAPI also provides interactive docs while the server is running:

```text
http://127.0.0.1:3000/docs
```

## API Key

Read endpoints require an API key header:

```text
X-API-Key: homework-api-key
```

The default key is defined in `main.py`. You can override it locally:

```bash
export BANKING_API_KEY="your-local-key"
./demo/run.sh
```

`POST /transactions` does not require the API key because this homework focuses the simple access-control example on account-data reads.

## Run Unit Tests

After installing dependencies:

```bash
cd homework-1
PYTHONPATH=src pytest -q
```

Current test coverage includes:

- API endpoint behavior
- business validation rules
- malformed and missing input cases
- unauthorized read access
- balance and summary calculations
- transaction filtering
- overdraft prevention
- edge cases such as zero amount, one-cent amount, malformed dates, and invalid filter values

## Demo Requests

Start the server, then run:

```bash
cd homework-1
./demo/sample-requests.sh
```

The script creates a deposit, creates a transfer, lists transactions, filters transaction history, gets a balance, and gets an account summary.

## Data Models

### Transaction Request

Used by `POST /transactions`.

```json
{
  "fromAccount": "ACC-12345",
  "toAccount": "ACC-67890",
  "amount": 100.5,
  "currency": "USD",
  "type": "transfer"
}
```

Fields:

- `fromAccount`: string or `null`
- `toAccount`: string or `null`
- `amount`: positive number with at most 2 decimal places
- `currency`: supported currency code
- `type`: `deposit`, `withdrawal`, or `transfer`

### Transaction Response

```json
{
  "id": "52d282ce-fcaf-42fb-b561-60fda0fdd498",
  "fromAccount": "ACC-12345",
  "toAccount": "ACC-67890",
  "amount": 100.5,
  "currency": "USD",
  "type": "transfer",
  "timestamp": "2026-07-05T18:19:16.825338Z",
  "status": "completed"
}
```

The API generates `id`, `timestamp`, and `status`.

## API Documentation

### Create Transaction

```http
POST /transactions
Content-Type: application/json
```

Deposit example:

```bash
curl -X POST http://127.0.0.1:3000/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": null,
    "toAccount": "ACC-12345",
    "amount": 250.00,
    "currency": "USD",
    "type": "deposit"
  }'
```

Successful response: `201 Created`

```json
{
  "id": "52d282ce-fcaf-42fb-b561-60fda0fdd498",
  "fromAccount": null,
  "toAccount": "ACC-12345",
  "amount": 250,
  "currency": "USD",
  "type": "deposit",
  "timestamp": "2026-07-05T18:19:16.825338Z",
  "status": "completed"
}
```

Expected status codes:

- `201`: transaction created
- `400`: business validation failed
- `422`: malformed JSON or schema-level request error
- `500`: unexpected internal error

### List Transactions

```http
GET /transactions
X-API-Key: homework-api-key
```

Example:

```bash
curl http://127.0.0.1:3000/transactions \
  -H "X-API-Key: homework-api-key"
```

Successful response: `200 OK`

```json
[
  {
    "id": "52d282ce-fcaf-42fb-b561-60fda0fdd498",
    "fromAccount": null,
    "toAccount": "ACC-12345",
    "amount": 250,
    "currency": "USD",
    "type": "deposit",
    "timestamp": "2026-07-05T18:19:16.825338Z",
    "status": "completed"
  }
]
```

Supported filters:

```text
?accountId=ACC-12345
?type=deposit
?from=2026-01-01
?to=2026-12-31
```

Filters can be combined:

```bash
curl "http://127.0.0.1:3000/transactions?accountId=ACC-12345&type=transfer&from=2026-01-01&to=2026-12-31" \
  -H "X-API-Key: homework-api-key"
```

Expected status codes:

- `200`: transactions returned
- `400`: invalid business-level filter, such as `from` date after `to` date
- `401`: missing or invalid API key
- `422`: malformed date or invalid transaction type query value
- `500`: unexpected internal error

### Get Transaction by ID

```http
GET /transactions/{transaction_id}
X-API-Key: homework-api-key
```

Example:

```bash
curl http://127.0.0.1:3000/transactions/52d282ce-fcaf-42fb-b561-60fda0fdd498 \
  -H "X-API-Key: homework-api-key"
```

Successful response: `200 OK`

```json
{
  "id": "52d282ce-fcaf-42fb-b561-60fda0fdd498",
  "fromAccount": null,
  "toAccount": "ACC-12345",
  "amount": 250,
  "currency": "USD",
  "type": "deposit",
  "timestamp": "2026-07-05T18:19:16.825338Z",
  "status": "completed"
}
```

Expected status codes:

- `200`: transaction found
- `401`: missing or invalid API key
- `404`: transaction ID not found
- `500`: unexpected internal error

### Get Account Balance

```http
GET /accounts/{account_id}/balance
X-API-Key: homework-api-key
```

Example:

```bash
curl http://127.0.0.1:3000/accounts/ACC-12345/balance \
  -H "X-API-Key: homework-api-key"
```

Successful response: `200 OK`

```json
{
  "accountId": "ACC-12345",
  "balance": 149.5,
  "currency": "USD"
}
```

Balance rules:

- deposits add to `toAccount`
- withdrawals subtract from `fromAccount`
- transfers subtract from `fromAccount` and add to `toAccount`
- accounts without transactions return `0.0` and default currency `USD`

Expected status codes:

- `200`: balance returned
- `401`: missing or invalid API key
- `500`: unexpected internal error

### Get Account Summary

```http
GET /accounts/{account_id}/summary
X-API-Key: homework-api-key
```

Example:

```bash
curl http://127.0.0.1:3000/accounts/ACC-12345/summary \
  -H "X-API-Key: homework-api-key"
```

Successful response: `200 OK`

```json
{
  "accountId": "ACC-12345",
  "totalDeposits": 250,
  "totalWithdrawals": 100.5,
  "transactionCount": 2,
  "mostRecentTransactionDate": "2026-07-05T18:19:16.825338Z"
}
```

For an account with no transactions:

```json
{
  "accountId": "ACC-99999",
  "totalDeposits": 0,
  "totalWithdrawals": 0,
  "transactionCount": 0,
  "mostRecentTransactionDate": null
}
```

Expected status codes:

- `200`: summary returned
- `401`: missing or invalid API key
- `500`: unexpected internal error

## Error Handling

### Business Validation Errors

Business-rule failures return `400 Bad Request`:

```json
{
  "error": "Validation failed",
  "details": [
    {
      "field": "amount",
      "message": "Amount must be a positive number"
    }
  ]
}
```

Examples:

- amount is zero or negative
- amount has more than 2 decimal places
- invalid account number format
- unsupported currency
- transfer source and destination are the same
- withdrawal or transfer would overdraw the source account
- date filter has `from` later than `to`

### Schema and Parsing Errors

Malformed JSON, missing required fields, invalid enum values, or malformed date query parameters return `422 Unprocessable Entity`.

Example missing `amount`:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "amount"],
      "msg": "Field required"
    }
  ]
}
```

The exact `detail` fields are generated by FastAPI/Pydantic.

### Unauthorized Read Access

Protected read endpoints return `401 Unauthorized` when `X-API-Key` is missing or incorrect:

```json
{
  "detail": "Missing or invalid API key"
}
```

### Not Found

Unknown transaction IDs return `404 Not Found`:

```json
{
  "detail": "Transaction not found"
}
```

### Unexpected Errors

Unexpected exceptions return:

```json
{
  "detail": "Internal server error"
}
```

This avoids exposing stack traces or internal implementation details to API clients.

## Validation Rules

### Amount

- required
- must be positive
- must have at most 2 decimal places
- handled internally using `Decimal`

### Accounts

Account numbers must match:

```text
ACC-XXXXX
```

`X` must be an uppercase letter or digit. Examples:

- valid: `ACC-12345`
- valid: `ACC-A1B2C`
- invalid: `12345`
- invalid: `ACC-1234`
- invalid: `acc-12345`

### Currency

Supported currencies:

```text
USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY, UAH
```

The API normalizes accepted currencies to uppercase before storing transactions.

### Transaction Types

`deposit`:

- requires `toAccount`
- must not include `fromAccount`

`withdrawal`:

- requires `fromAccount`
- must not include `toAccount`
- cannot overdraw the source account

`transfer`:

- requires both `fromAccount` and `toAccount`
- source and destination must be different
- cannot overdraw the source account

## Security Considerations

Implemented:

- API key required for endpoints that expose transaction history or account data
- constant-time API key comparison with `secrets.compare_digest`
- no full request-body logging
- generic `500` error response for unexpected failures
- structured validation errors without stack traces
- overdraft prevention for withdrawals and transfers
- Decimal-based money calculations to avoid binary floating-point balance errors

Not implemented because this is a homework project:

- user accounts or real authentication
- authorization by account owner
- persistent database storage
- encryption at rest
- audit logging
- rate limiting
- idempotency keys for duplicate transaction prevention
- HTTPS termination
- production secrets management

## Assumptions and Limitations

- Storage is in memory. All data is lost when the server restarts.
- The API key is a simple homework-level control, not production authentication.
- `POST /transactions` is intentionally public in this implementation; read endpoints are protected.
- There is no concept of registered accounts. Any valid account ID format can be used.
- Accounts without transactions return a zero USD balance.
- The service assumes all transactions for an account use the latest matching transaction currency for balance display.
- Transaction status is always set to `completed`.
- There are no pending or failed transaction workflows.
- There is no concurrency control around the in-memory store.
- API examples use localhost and are intended for local development only.

## Screenshots

Course submission screenshots should be placed in:

```text
homework-1/docs/screenshots/
```

Suggested screenshots:

- API running locally
- sample curl requests and responses
- pytest output
- AI-assisted development prompts or workflow evidence
