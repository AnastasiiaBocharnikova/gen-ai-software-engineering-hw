from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, File, HTTPException, Query, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from support_tickets.classification import ClassificationResult, classify_ticket
from support_tickets.importers import ImportParseError, parse_ticket_file
from support_tickets.models import (
    ImportSummary,
    TicketCategory,
    TicketCreate,
    TicketPriority,
    TicketResponse,
    TicketStatus,
    TicketUpdate,
)
from support_tickets.services import import_ticket_records
from support_tickets.store import TicketStore


ticket_store = TicketStore()

app = FastAPI(
    title="Intelligent Customer Support System",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error": "NotFound",
            "message": "ticket not found",
            "details": [],
        },
    )


def bad_import_request(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "error": "ImportParseError",
            "message": message,
            "details": [],
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return fastapi_json_response(exc.status_code, exc.detail)
    return fastapi_json_response(
        exc.status_code,
        {
            "error": "HTTPException",
            "message": str(exc.detail),
            "details": [],
        },
    )


def fastapi_json_response(status_code: int, content: dict):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=status_code, content=content)


@app.post(
    "/tickets",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(ticket: TicketCreate) -> TicketResponse:
    return ticket_store.create(ticket)


@app.get("/tickets", response_model=list[TicketResponse])
def list_tickets(
    category: Optional[TicketCategory] = Query(default=None),
    priority: Optional[TicketPriority] = Query(default=None),
    status_filter: Optional[TicketStatus] = Query(default=None, alias="status"),
) -> list[TicketResponse]:
    return ticket_store.list(
        category=category,
        priority=priority,
        status=status_filter,
    )


@app.post(
    "/tickets/import",
    response_model=ImportSummary,
    status_code=status.HTTP_201_CREATED,
)
async def import_tickets(
    file_format: str = Query(alias="format"),
    file: UploadFile = File(...),
    auto_classify: bool = Query(default=False),
) -> ImportSummary:
    content = await file.read()
    try:
        records = parse_ticket_file(file_format, content)
    except ImportParseError as exc:
        raise bad_import_request(str(exc)) from exc

    return import_ticket_records(records, ticket_store, auto_classify=auto_classify)


@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str) -> TicketResponse:
    ticket = ticket_store.get(ticket_id)
    if ticket is None:
        raise not_found()
    return ticket


@app.put("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: str, ticket_update: TicketUpdate) -> TicketResponse:
    ticket = ticket_store.update(ticket_id, ticket_update)
    if ticket is None:
        raise not_found()
    return ticket


@app.post("/tickets/{ticket_id}/auto-classify", response_model=ClassificationResult)
def auto_classify_ticket(ticket_id: str) -> ClassificationResult:
    ticket = ticket_store.get(ticket_id)
    if ticket is None:
        raise not_found()

    result = classify_ticket(ticket)
    ticket_store.apply_classification(
        ticket_id,
        category=result.category,
        priority=result.priority,
        confidence=result.confidence,
        reasoning=result.reasoning,
        keywords=result.keywords_found,
    )
    return result


@app.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: str) -> Response:
    deleted = ticket_store.delete(ticket_id)
    if not deleted:
        raise not_found()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
