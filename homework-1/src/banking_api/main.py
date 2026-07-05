from __future__ import annotations

import os
import secrets
from datetime import date
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from banking_api.models import AccountBalance, AccountSummary, Transaction, TransactionCreate, TransactionType
from banking_api.services import calculate_account_summary, calculate_balance, create_transaction, filter_transactions
from banking_api.store import TransactionStore
from banking_api.validation import BusinessValidationError, validation_response

API_KEY = os.getenv("BANKING_API_KEY", "homework-api-key")

app = FastAPI(title="Banking Transactions API")
store = TransactionStore()


def reset_store_for_tests() -> None:
    store.clear()


def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> None:
    if not x_api_key or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401, detail="Missing or invalid API key")


@app.exception_handler(BusinessValidationError)
async def business_validation_exception_handler(
    request: Request, exc: BusinessValidationError
) -> JSONResponse:
    return JSONResponse(status_code=400, content=validation_response(exc.details))


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": jsonable_encoder(exc.errors())})


@app.exception_handler(Exception)
async def unexpected_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.post("/transactions", response_model=Transaction, status_code=201)
def post_transaction(payload: TransactionCreate) -> Transaction:
    return create_transaction(payload, store)


@app.get("/transactions", response_model=list[Transaction], dependencies=[Depends(require_api_key)])
def get_transactions(
    account_id: Optional[str] = Query(default=None, alias="accountId"),
    transaction_type: Optional[TransactionType] = Query(default=None, alias="type"),
    from_date: Optional[date] = Query(default=None, alias="from"),
    to_date: Optional[date] = Query(default=None, alias="to"),
) -> list[Transaction]:
    return filter_transactions(store.list(), account_id, transaction_type, from_date, to_date)


@app.get("/transactions/{transaction_id}", response_model=Transaction, dependencies=[Depends(require_api_key)])
def get_transaction(transaction_id: str) -> Transaction:
    transaction = store.get(transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.get("/accounts/{account_id}/balance", response_model=AccountBalance, dependencies=[Depends(require_api_key)])
def get_account_balance(account_id: str) -> AccountBalance:
    return calculate_balance(account_id, store.list())


@app.get("/accounts/{account_id}/summary", response_model=AccountSummary, dependencies=[Depends(require_api_key)])
def get_account_summary(account_id: str) -> AccountSummary:
    return calculate_account_summary(account_id, store.list())
