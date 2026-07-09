# AI Usage

## Tools Used

- Codex for implementation planning, code generation, test generation, documentation drafting, and verification.

## Models Used

- Codex GPT-5 coding agent in the local Codex desktop environment.

The assignment asks to use different AI models for different document types. In this implementation session, Codex was the available AI assistant used for all generated code and documentation. The generated documentation was manually reviewed and edited for consistency with the actual implementation.

## AI-Assisted Work

Codex helped with:

- analyzing `TASKS.md`, `AGENTS.md`, and `HOMEWORK_STANDARDS.md`
- planning the implementation order
- generating FastAPI models, routes, importers, classifier, and store
- generating React frontend code
- generating unit, API, integration, negative, sample data, and performance tests
- drafting README, API reference, architecture, testing, and AI usage docs
- running verification commands and interpreting failures

## Prompt Patterns Used

- "Review the assignment scope and create a detailed plan."
- "Proceed with the next point."
- "Add negative verification."
- "Web preview doesn't work."

## Manual Review and Changes

Manual corrections made after AI output:

- Pinned Vite and React dependencies to Node 18-compatible versions.
- Restarted the backend with `PYTHONPATH=src` after preview import errors.
- Verified the React UI through the in-app browser at the correct frontend URL.
- Kept generated artifacts such as `.venv`, `.pytest_cache`, `node_modules`, and `dist` ignored.

## Verification Evidence

Latest backend test command:

```bash
PYTHONPATH=src .venv/bin/pytest -q
```

Latest verified result:

```text
74 passed
```

Latest frontend build command:

```bash
npm run build
```

Latest verified result:

```text
✓ built
```
