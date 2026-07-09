# API Reference

Base URL for local development:

```text
http://127.0.0.1:3000
```

## Error Format

Application-defined errors use this shape:

```json
{
  "error": "NotFound",
  "message": "ticket not found",
  "details": []
}
```

FastAPI validation errors use the standard `422` response with a `detail` array.

## Ticket Model

```json
{
  "id": "UUID",
  "customer_id": "cust-123",
  "customer_email": "customer@example.com",
  "customer_name": "Ada Lovelace",
  "subject": "Cannot access account",
  "description": "I cannot access my account after changing my password.",
  "category": "account_access",
  "priority": "urgent",
  "status": "new",
  "created_at": "2026-07-07T12:00:00Z",
  "updated_at": "2026-07-07T12:00:00Z",
  "resolved_at": null,
  "assigned_to": null,
  "tags": ["login", "password"],
  "metadata": {
    "source": "web_form",
    "browser": "Chrome",
    "device_type": "desktop"
  },
  "classification_confidence": 0.95,
  "classification_reasoning": "Matched account_access category and urgent priority using keywords: cannot access, password.",
  "classification_keywords": ["cannot access", "password"],
  "classification_overridden": false
}
```

Enums:

- `category`: `account_access`, `technical_issue`, `billing_question`, `feature_request`, `bug_report`, `other`
- `priority`: `urgent`, `high`, `medium`, `low`
- `status`: `new`, `in_progress`, `waiting_customer`, `resolved`, `closed`
- `metadata.source`: `web_form`, `email`, `api`, `chat`, `phone`
- `metadata.device_type`: `desktop`, `mobile`, `tablet`

## Create Ticket

```http
POST /tickets
Content-Type: application/json
```

Request:

```json
{
  "customer_id": "cust-123",
  "customer_email": "customer@example.com",
  "customer_name": "Ada Lovelace",
  "subject": "Cannot access account",
  "description": "I cannot access my account after changing my password.",
  "metadata": {
    "source": "web_form",
    "browser": "Chrome",
    "device_type": "desktop"
  },
  "tags": ["login", "password"]
}
```

Response: `201 Created`

```bash
curl -X POST http://127.0.0.1:3000/tickets \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"cust-123","customer_email":"customer@example.com","customer_name":"Ada Lovelace","subject":"Cannot access account","description":"I cannot access my account after changing my password.","metadata":{"source":"web_form","browser":"Chrome","device_type":"desktop"},"tags":["login","password"]}'
```

## List Tickets

```http
GET /tickets
GET /tickets?category=billing_question&priority=high&status=in_progress
```

Response: `200 OK`

```bash
curl "http://127.0.0.1:3000/tickets?category=billing_question&priority=high"
```

## Get Ticket

```http
GET /tickets/{ticket_id}
```

Response: `200 OK` or `404 Not Found`

```bash
curl http://127.0.0.1:3000/tickets/{ticket_id}
```

## Update Ticket

```http
PUT /tickets/{ticket_id}
Content-Type: application/json
```

Request:

```json
{
  "status": "in_progress",
  "assigned_to": "agent-1",
  "priority": "high"
}
```

Response: `200 OK`, `404 Not Found`, or `422 Unprocessable Entity`

```bash
curl -X PUT http://127.0.0.1:3000/tickets/{ticket_id} \
  -H "Content-Type: application/json" \
  -d '{"status":"in_progress","assigned_to":"agent-1"}'
```

Changing `category` or `priority` through this endpoint marks `classification_overridden` as `true`.

## Delete Ticket

```http
DELETE /tickets/{ticket_id}
```

Response: `204 No Content` or `404 Not Found`

```bash
curl -X DELETE http://127.0.0.1:3000/tickets/{ticket_id}
```

## Auto-Classify Ticket

```http
POST /tickets/{ticket_id}/auto-classify
```

Response:

```json
{
  "category": "account_access",
  "priority": "urgent",
  "confidence": 0.95,
  "reasoning": "Matched account_access category and urgent priority using keywords: cannot access, password.",
  "keywords_found": ["cannot access", "password"]
}
```

```bash
curl -X POST http://127.0.0.1:3000/tickets/{ticket_id}/auto-classify
```

## Bulk Import Tickets

```http
POST /tickets/import?format=csv
POST /tickets/import?format=json
POST /tickets/import?format=xml
POST /tickets/import?format=json&auto_classify=true
```

Request: multipart form upload with field `file`.

Response: `201 Created`

```json
{
  "total_records": 2,
  "successful": 1,
  "failed": 1,
  "errors": [
    {
      "record_number": 2,
      "message": "validation error details"
    }
  ],
  "created_ticket_ids": ["generated-ticket-id"]
}
```

```bash
curl -X POST "http://127.0.0.1:3000/tickets/import?format=csv&auto_classify=true" \
  -F "file=@sample_data/valid/sample_tickets.csv"
```

Malformed files and unsupported formats return `400 Bad Request`.
