from __future__ import annotations

from pydantic import ValidationError

from support_tickets.classification import classify_ticket
from support_tickets.models import ImportErrorDetail, ImportSummary, TicketCreate
from support_tickets.store import TicketStore


def import_ticket_records(
    records: list[dict],
    store: TicketStore,
    *,
    auto_classify: bool = False,
) -> ImportSummary:
    errors: list[ImportErrorDetail] = []
    created_ticket_ids: list[str] = []

    for index, record in enumerate(records, start=1):
        try:
            ticket_create = TicketCreate(**record)
        except ValidationError as exc:
            errors.append(ImportErrorDetail(record_number=index, message=str(exc)))
            continue

        created = store.create(ticket_create)
        if auto_classify:
            result = classify_ticket(created)
            classified = store.apply_classification(
                created.id,
                category=result.category,
                priority=result.priority,
                confidence=result.confidence,
                reasoning=result.reasoning,
                keywords=result.keywords_found,
            )
            created_ticket_ids.append(classified.id if classified else created.id)
        else:
            created_ticket_ids.append(created.id)

    return ImportSummary(
        total_records=len(records),
        successful=len(created_ticket_ids),
        failed=len(errors),
        errors=errors,
        created_ticket_ids=created_ticket_ids,
    )
