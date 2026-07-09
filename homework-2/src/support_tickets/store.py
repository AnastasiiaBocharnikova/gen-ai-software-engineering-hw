from __future__ import annotations

from datetime import timedelta
from threading import RLock
from typing import Optional

from support_tickets.models import (
    TicketCategory,
    TicketCreate,
    TicketPriority,
    TicketResponse,
    TicketStatus,
    TicketUpdate,
    utc_now,
)


class TicketStore:
    def __init__(self) -> None:
        self._tickets: dict[str, TicketResponse] = {}
        self._order: list[str] = []
        self._lock = RLock()

    def create(self, ticket: TicketCreate) -> TicketResponse:
        with self._lock:
            stored = TicketResponse.from_create(ticket)
            self._tickets[stored.id] = stored
            self._order.append(stored.id)
            return stored

    def get(self, ticket_id: str) -> Optional[TicketResponse]:
        with self._lock:
            return self._tickets.get(ticket_id)

    def list(
        self,
        *,
        category: Optional[TicketCategory] = None,
        priority: Optional[TicketPriority] = None,
        status: Optional[TicketStatus] = None,
    ) -> list[TicketResponse]:
        with self._lock:
            tickets = [self._tickets[ticket_id] for ticket_id in self._order]

        if category is not None:
            tickets = [ticket for ticket in tickets if ticket.category == category]
        if priority is not None:
            tickets = [ticket for ticket in tickets if ticket.priority == priority]
        if status is not None:
            tickets = [ticket for ticket in tickets if ticket.status == status]
        return tickets

    def update(
        self, ticket_id: str, changes: TicketUpdate | dict
    ) -> Optional[TicketResponse]:
        with self._lock:
            existing = self._tickets.get(ticket_id)
            if existing is None:
                return None

            update = changes if isinstance(changes, TicketUpdate) else TicketUpdate(**changes)
            values = update.model_dump(exclude_unset=True)
            now = utc_now()
            if now <= existing.updated_at:
                now = existing.updated_at + timedelta(microseconds=1)

            values["updated_at"] = now
            if values.get("status") == "resolved" and existing.resolved_at is None:
                values["resolved_at"] = now
            if values.get("status") in {"new", "in_progress", "waiting_customer"}:
                values["resolved_at"] = None
            category_changed = (
                "category" in values and values["category"] != existing.category
            )
            priority_changed = (
                "priority" in values and values["priority"] != existing.priority
            )
            if category_changed or priority_changed:
                values["classification_overridden"] = True

            updated = existing.model_copy(update=values)
            self._tickets[ticket_id] = updated
            return updated

    def apply_classification(
        self,
        ticket_id: str,
        *,
        category: TicketCategory,
        priority: TicketPriority,
        confidence: float,
        reasoning: str,
        keywords: list[str],
    ) -> Optional[TicketResponse]:
        with self._lock:
            existing = self._tickets.get(ticket_id)
            if existing is None:
                return None

            now = utc_now()
            if now <= existing.updated_at:
                now = existing.updated_at + timedelta(microseconds=1)

            updated = existing.model_copy(
                update={
                    "category": category,
                    "priority": priority,
                    "classification_confidence": confidence,
                    "classification_reasoning": reasoning,
                    "classification_keywords": keywords,
                    "classification_overridden": False,
                    "updated_at": now,
                }
            )
            self._tickets[ticket_id] = updated
            return updated

    def delete(self, ticket_id: str) -> bool:
        with self._lock:
            if ticket_id not in self._tickets:
                return False
            del self._tickets[ticket_id]
            self._order.remove(ticket_id)
            return True

    def reset(self) -> None:
        with self._lock:
            self._tickets.clear()
            self._order.clear()
