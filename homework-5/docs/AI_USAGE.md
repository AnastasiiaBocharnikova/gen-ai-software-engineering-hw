# AI Usage

## Tools used

- OpenAI Codex app and CLI
- GPT-5.6 Sol
- Official Codex and GitHub MCP documentation

## How AI assisted

- Reviewed the assignment and repository standards.
- Compared supported GitHub MCP connection methods.
- Prepared a project-scoped Codex MCP configuration.
- Added reproducible setup, verification, and demonstration instructions.
- Checked that committed configuration contains no GitHub credential.

## Important prompt pattern

The Task 1 demonstration uses a constrained, read-only prompt that names the MCP server, repository, requested fields, result limit, and prohibition on writes:

```text
Using only the GitHub MCP server, list the five most recent pull requests
for AnastasiiaBocharnikova/gen-ai-software-engineering-hw. For each one,
show its number, title, state, author, and URL. Then briefly summarize the
most recent pull request. Do not create or modify anything.
```

## Manual work and review

- The repository owner supplies the fine-grained GitHub token outside version control.
- MCP authorization and project trust are approved manually in Codex.
- The returned repository data and screenshot are manually reviewed for accuracy, readability, and sensitive information before submission.
