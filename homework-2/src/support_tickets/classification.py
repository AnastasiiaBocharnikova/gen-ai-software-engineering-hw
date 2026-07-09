from __future__ import annotations

from pydantic import BaseModel, Field

from support_tickets.models import TicketCategory, TicketCreate, TicketPriority


class ClassificationResult(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    confidence: float = Field(ge=0, le=1)
    reasoning: str
    keywords_found: list[str]


CATEGORY_KEYWORDS: list[tuple[TicketCategory, list[str]]] = [
    ("bug_report", ["steps to reproduce", "reproduce", "defect"]),
    ("account_access", ["login", "password", "2fa", "two-factor", "cannot access"]),
    ("billing_question", ["payment", "invoice", "refund", "billing"]),
    ("feature_request", ["enhancement", "suggestion", "feature request", "add"]),
    ("technical_issue", ["bug", "error", "crash", "crashes", "failed"]),
]

PRIORITY_KEYWORDS: list[tuple[TicketPriority, list[str]]] = [
    ("urgent", ["can't access", "cannot access", "critical", "production down", "security"]),
    ("high", ["important", "blocking", "asap"]),
    ("low", ["minor", "cosmetic", "suggestion"]),
]


def classify_ticket(ticket: TicketCreate) -> ClassificationResult:
    text = f"{ticket.subject} {ticket.description}".lower()
    category, category_keywords = _classify_category(text)
    priority, priority_keywords = _classify_priority(text)
    keywords_found = _unique(category_keywords + priority_keywords)
    confidence = _confidence(category, keywords_found)

    if keywords_found:
        reasoning = (
            f"Matched {category} category and {priority} priority using keywords: "
            f"{', '.join(keywords_found)}."
        )
    else:
        reasoning = "No specific classification keywords found; using default category and priority."

    return ClassificationResult(
        category=category,
        priority=priority,
        confidence=confidence,
        reasoning=reasoning,
        keywords_found=keywords_found,
    )


def _classify_category(text: str) -> tuple[TicketCategory, list[str]]:
    for category, keywords in CATEGORY_KEYWORDS:
        matches = [keyword for keyword in keywords if keyword in text]
        if matches:
            return category, matches
    return "other", []


def _classify_priority(text: str) -> tuple[TicketPriority, list[str]]:
    for priority, keywords in PRIORITY_KEYWORDS:
        matches = [keyword for keyword in keywords if keyword in text]
        if matches:
            return priority, matches
    return "medium", []


def _confidence(category: TicketCategory, keywords_found: list[str]) -> float:
    if not keywords_found:
        return 0.35
    if category == "other":
        return 0.55
    return min(0.95, 0.65 + (0.1 * len(keywords_found)))


def _unique(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
