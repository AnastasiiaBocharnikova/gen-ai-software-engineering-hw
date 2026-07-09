# AGENTS.md

## General Style

- Keep explanations brief and practical.
- Prefer concrete actions over long theory.
- Before implementing larger changes, briefly explain the plan.

## Repository Rules

- Treat each `homework-N/` folder as an independent assignment.
- Use `HOMEWORK_STANDARDS.md` as the shared checklist for all homework tasks.
- Do not mix files between homework folders unless explicitly asked.
- Preserve existing user changes.

## Implementation Preferences

- Prefer simple, maintainable solutions over complex abstractions.
- Follow the stack already used in the homework folder.
- If no stack exists, recommend the fastest practical stack for the assignment.
- Keep generated code readable and easy to explain.

## Testing Rules

- Add or update tests for meaningful behavior changes.
- Aim for coverage required by the assignment, usually `>85%`.
- Run relevant tests before saying work is complete.
- If tests cannot be run, clearly say why.

## Documentation Rules

- Keep README and docs aligned with the actual implementation.
- Add setup, run, test, and coverage instructions.
- For API projects, document endpoints, examples, errors, and status codes.
- For course assignments, maintain `docs/AI_USAGE.md` when relevant.

## Pull Request Rules

- Create a detailed PR summary for every pull request.
- The PR summary should explain what changed, why it changed, how it was tested, and any known limitations.
- Include relevant screenshots for UI changes, coverage reports, or visible deliverables.
- Attach screenshots directly in the PR description using HTML image tags that point to committed GitHub files with `?raw=true`, for example:

```html
<img width="900" alt="unauthorized-access" src="https://github.com/AnastasiiaBocharnikova/gen-ai-software-engineering-hw/blob/69a99c49d0ed4a61161f4435a7a73af9ddba81d9/homework-1/docs/screenshots/Postman_401.png?raw=true" />
```
- When showing local screenshots in Codex responses before PR creation, use absolute filesystem paths.

## Git Rules

- Do not revert user changes without explicit permission.
- Do not run destructive git commands unless explicitly requested.
- Mention changed files in the final response.
