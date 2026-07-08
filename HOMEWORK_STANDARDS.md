# Homework Standards

Use this checklist for every homework assignment in this repository.

## Project Structure

Each homework should follow this structure where applicable:

```text
homework-N/
├── README.md
├── TASKS.md
├── src/
├── tests/
├── docs/
│   ├── API_REFERENCE.md
│   ├── ARCHITECTURE.md
│   ├── TESTING_GUIDE.md
│   ├── AI_USAGE.md
│   └── screenshots/
├── sample_data/
│   ├── valid/
│   └── invalid/
└── requirements.txt / package.json / pyproject.toml
```

Adjust the structure if the assignment does not need backend, frontend, API docs, or sample files.

## README Standard

Every homework `README.md` should include:

- Project overview
- Main features
- Chosen tech stack
- Setup instructions
- How to run the app
- How to run tests
- How to check coverage
- Project structure
- Sample data locations
- Screenshot locations

## Testing Standard

Every homework should include tests that match the assignment scope:

- Unit tests for core logic
- API tests for endpoints
- Integration tests for full workflows
- Negative tests for invalid input
- Fixture files for repeatable test data
- Performance tests when required

Default target:

```text
Coverage: >85%
```

Coverage evidence should be saved when required:

```text
docs/screenshots/test_coverage.png
```

## Documentation Standard

When the assignment requires documentation, include:

```text
README.md
docs/API_REFERENCE.md
docs/ARCHITECTURE.md
docs/TESTING_GUIDE.md
docs/AI_USAGE.md
```

Use `docs/AI_USAGE.md` to record:

- AI tools used
- Models used, if relevant
- What each tool helped generate or improve
- Important prompts or prompt patterns
- Manual changes made after AI output

## API Standard

For backend/API assignments, document:

- All endpoints
- Request examples
- Response examples
- Validation rules
- Error response format
- HTTP status codes
- cURL examples

Use a consistent error shape, for example:

```json
{
  "error": "ValidationError",
  "message": "customer_email must be a valid email",
  "details": []
}
```

## Frontend Standard

For frontend assignments, the UI should:

- Use the real API when a backend exists
- Avoid hardcoded production-like data
- Show loading states
- Show error states
- Show success feedback
- Work on desktop and mobile
- Include client-side validation for forms

Save a representative screenshot when required:

```text
docs/screenshots/ui.png
```

## Sample Data Standard

Keep sample files separate from source code:

```text
sample_data/
├── valid/
└── invalid/
```

Valid files should support demos and integration tests.
Invalid files should support negative tests.

## Mermaid Diagrams

When documentation asks for diagrams, prefer Mermaid:

- Architecture diagram in `ARCHITECTURE.md`
- API or request flow diagram
- Test pyramid or workflow diagram in `TESTING_GUIDE.md`

## Pre-Submission Checklist

Before considering a homework complete:

- App starts successfully
- Tests pass
- Coverage target is met
- README is accurate
- API docs match implementation
- Architecture docs match implementation
- Sample data is present
- Invalid sample data is present when needed
- Screenshots are saved when required
- No generated cache/build artifacts are committed unless required

