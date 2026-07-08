from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field


TicketCategory = Literal[
    "account_access",
    "technical_issue",
    "billing_question",
    "feature_request",
    "bug_report",
    "other",
]
TicketPriority = Literal["urgent", "high", "medium", "low"]
TicketStatus = Literal[
    "new",
    "in_progress",
    "waiting_customer",
    "resolved",
    "closed",
]
TicketSource = Literal["web_form", "email", "api", "chat", "phone"]
DeviceType = Literal["desktop", "mobile", "tablet"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TicketMetadata(BaseModel):
    source: TicketSource
    browser: str = Field(default="", max_length=100)
    device_type: DeviceType


class TicketCreate(BaseModel):
    customer_id: str = Field(min_length=1, max_length=100)
    customer_email: EmailStr
    customer_name: str = Field(min_length=1, max_length=120)
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    category: TicketCategory = "other"
    priority: TicketPriority = "medium"
    status: TicketStatus = "new"
    assigned_to: Optional[str] = Field(default=None, max_length=120)
    tags: list[str] = Field(default_factory=list)
    metadata: TicketMetadata


class TicketUpdate(BaseModel):
    customer_id: Optional[str] = Field(default=None, min_length=1, max_length=100)
    customer_email: Optional[EmailStr] = None
    customer_name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    subject: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, min_length=10, max_length=2000)
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assigned_to: Optional[str] = Field(default=None, max_length=120)
    tags: Optional[list[str]] = None
    metadata: Optional[TicketMetadata] = None


class TicketResponse(TicketCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    classification_confidence: Optional[float] = Field(default=None, ge=0, le=1)
    classification_reasoning: Optional[str] = None
    classification_keywords: list[str] = Field(default_factory=list)
    classification_overridden: bool = False

    @classmethod
    def from_create(cls, ticket: TicketCreate) -> "TicketResponse":
        now = utc_now()
        return cls(
            **ticket.model_dump(),
            id=str(uuid4()),
            created_at=now,
            updated_at=now,
        )


class ImportErrorDetail(BaseModel):
    record_number: int
    message: str


class ImportSummary(BaseModel):
    total_records: int
    successful: int
    failed: int
    errors: list[ImportErrorDetail] = Field(default_factory=list)
    created_ticket_ids: list[str] = Field(default_factory=list)
