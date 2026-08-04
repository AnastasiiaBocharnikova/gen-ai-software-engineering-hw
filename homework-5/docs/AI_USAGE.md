# AI Usage

## Tools used

- OpenAI Codex app and CLI
- GPT-5.6 Sol
- Official Codex, GitHub MCP, and Filesystem MCP documentation

## How AI assisted

- Reviewed the assignment and repository standards.
- Compared supported GitHub MCP connection methods.
- Prepared a project-scoped Codex MCP configuration.
- Added reproducible setup, verification, and demonstration instructions.
- Checked that committed configuration contains no GitHub credential.
- Scoped Filesystem MCP access to the Homework 5 directory.
- Restricted the Filesystem MCP tool allowlist to read-only operations needed by Task 2.

## Important prompt pattern

The Task 1 demonstration uses a constrained, read-only prompt that names the MCP server, repository, requested fields, result limit, and prohibition on writes:

```text
Using only the GitHub MCP server, list the five most recent pull requests
for AnastasiiaBocharnikova/gen-ai-software-engineering-hw. For each one,
show its number, title, state, author, and URL. Then briefly summarize the
most recent pull request. Do not create or modify anything.
```

The Task 2 prompt explicitly names the Filesystem MCP server, requests allowed-directory proof before reading, and prohibits filesystem mutations:

```text
Using only the Filesystem MCP server:

1. Show the allowed directories.
2. List the files and directories in the allowed Homework 5 directory.
3. Read TASKS.md and summarize the requirements of Task 2.
Do not create, edit, move, or delete anything.
```

## Manual work and review

- The repository owner supplies the fine-grained GitHub token outside version control.
- MCP authorization and project trust are approved manually in Codex.
- The returned repository data and screenshot are manually reviewed for accuracy, readability, and sensitive information before submission.
- The Filesystem MCP result is checked to confirm that only the intended Homework 5 directory is allowed.
