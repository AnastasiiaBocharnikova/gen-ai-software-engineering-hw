# AI Usage

## Tools and Models

Codex was used to analyze `TASKS.md`, design the pipeline, implement the sample
application, create custom agent profiles, and verify the submission. The agent
profiles explicitly use `gpt-5.6-sol` for reasoning-heavy verification,
planning, security, and orchestration, and `gpt-5.6-terra` for bounded
research, fixing, and test generation.

## Prompt Patterns

- “Verify every `file:line` reference and grade research with the supplied
  quality skill.”
- “Apply only the verified plan, run a focused test after each change, and stop
  on failure.”
- “Review changed code only; report severity and remediation without edits.”
- “Generate tests only for changed behavior and assess every FIRST property.”

## Manual Review and Changes

All agent contracts were checked against the assignment. Application work used
test-first cycles: tests were observed failing before production modules were
added. Report references were checked against numbered current source, model
profiles were checked against current official Codex custom-agent syntax, and
the complete local test and validation commands were run before submission.
