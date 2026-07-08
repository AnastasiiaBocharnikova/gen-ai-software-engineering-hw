# Architecture

## Overview

The system uses a small layered architecture. FastAPI exposes the ticket API, service functions coordinate workflows, Pydantic validates request and response models, a thread-safe in-memory store holds tickets, importers normalize CSV/JSON/XML files, and a rule-based classifier assigns category and priority.

The React frontend is a single-page agent workspace that talks to the API through `fetch`.

## Component Diagram

```mermaid
flowchart TB
    subgraph Frontend
        UI[React Agent Workspace]
        Forms[Create Edit Import Forms]
        Filters[Queue Filters]
    end

    subgraph Backend
        Routes[FastAPI Routes]
        Services[Workflow Services]
        Models[Pydantic Models]
        Store[TicketStore]
        Importers[CSV JSON XML Importers]
        Classifier[Keyword Classifier]
    end

    UI --> Routes
    Forms --> Routes
    Filters --> Routes
    Routes --> Services
    Routes --> Models
    Routes --> Store
    Routes --> Importers
    Routes --> Classifier
    Services --> Models
    Services --> Store
    Services --> Classifier
    Importers --> Models
    Classifier --> Store
```

## Backend Components

- `main.py`: FastAPI application, route handlers, CORS setup, and HTTP error mapping.
- `services.py`: workflow services for import validation, creation, and optional classification.
- `models.py`: ticket schemas, enums, import summary models, and response models.
- `store.py`: thread-safe in-memory CRUD store.
- `importers.py`: CSV, JSON, and XML parsing and normalization.
- `classification.py`: deterministic keyword classifier.

## Frontend Components

- `frontend/src/main.jsx`: React app, API calls, forms, filters, import flow, classification action.
- `frontend/src/styles.css`: responsive operational UI styling.
- `frontend/package.json`: Vite build and dev scripts.

## Ticket Lifecycle Flow

```mermaid
sequenceDiagram
    participant Agent
    participant UI as React UI
    participant API as FastAPI
    participant Store as TicketStore
    participant Classifier

    Agent->>UI: Submit ticket form
    UI->>API: POST /tickets
    API->>Store: create(ticket)
    Store-->>API: TicketResponse
    API-->>UI: 201 Created
    Agent->>UI: Click auto-classify
    UI->>API: POST /tickets/{id}/auto-classify
    API->>Classifier: classify_ticket(ticket)
    Classifier-->>API: category, priority, confidence
    API->>Store: apply_classification(...)
    API-->>UI: classification result
```

## Import Flow

```mermaid
sequenceDiagram
    participant Agent
    participant UI as React UI
    participant API as FastAPI
    participant Parser as Importers
    participant Service as Import Service
    participant Models as Pydantic
    participant Store

    Agent->>UI: Upload CSV/JSON/XML
    UI->>API: POST /tickets/import
    API->>Parser: parse_ticket_file(format, bytes)
    Parser-->>API: normalized records
    API->>Service: import_ticket_records(...)
    loop each record
        Service->>Models: TicketCreate(**record)
        alt valid
            Service->>Store: create(ticket)
        else invalid
            Service->>Service: append record error
        end
    end
    Service-->>API: import summary
    API-->>UI: import summary
```

## Design Decisions

- In-memory storage is used because the assignment does not require persistence.
- Classification is deterministic and rule-based, which keeps behavior testable and avoids external API keys.
- Import supports partial success so one bad record does not block valid tickets.
- React uses the real API only; the UI does not ship hardcoded ticket rows.
- Manual category or priority edits mark the ticket as a classification override.

## Security Considerations

- Pydantic validates all request payloads and enum values.
- XML parsing uses Python standard `xml.etree.ElementTree`; no external entity behavior is used.
- CORS is open for local assignment development. Production deployment should restrict allowed origins.
- File import accepts only parsed CSV, JSON, or XML formats and returns controlled parse errors.

## Performance Considerations

- The in-memory store is protected by `RLock` for concurrent test scenarios.
- Filtering is linear over stored tickets, acceptable for the assignment scope.
- Performance tests cover 100-ticket creation/import, 200-ticket filtering, 50-ticket classification, and 20 concurrent create requests.
