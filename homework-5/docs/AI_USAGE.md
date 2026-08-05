# AI Usage

## Tools used

- OpenAI Codex app and CLI
- GPT-5.6 Sol
- Official Codex, GitHub MCP, Filesystem MCP, and Atlassian Rovo MCP documentation

## How AI assisted

- Reviewed the assignment and repository standards.
- Compared supported GitHub MCP connection methods.
- Prepared a project-scoped Codex MCP configuration.
- Added reproducible setup, verification, and demonstration instructions.
- Checked that committed configuration contains no GitHub credential.
- Scoped Filesystem MCP access to the Homework 5 directory.
- Restricted the Filesystem MCP tool allowlist to read-only operations needed by Task 2.
- Selected Atlassian OAuth 2.1 so Jira credentials remain outside the repository.
- Limited the Jira result to ticket keys to avoid exposing sensitive issue content.
- Designed the custom FastMCP Resource, `read` Tool, validation, and tests.
- Used test-driven development to verify exact word limits before completing the server.

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

The Task 3 prompt uses explicit JQL, limits the result to five bugs, and requests ticket keys only:

```text
Using only the Jira MCP server, give me the last five bugs from project SCRUM
on https://anastasiiabocharnikova.atlassian.net.

Use JQL:
project = SCRUM AND issuetype = "Баг" ORDER BY created DESC

Return only the five ticket keys, newest first. Do not include summaries,
descriptions, names, emails, comments, or other potentially sensitive data.
Do not create or modify anything.
```

The Jira site uses the localized issue type name `Баг`, so the JQL uses that
exact value instead of `Bug`.

The Task 4 prompt verifies the custom Tool without changing files:

```text
Using only the custom_lorem MCP server, call the read tool with word_count set
to 30. Return the tool result and state the exact number of returned words. Do
not modify any files.
```

## Manual work and review

- The repository owner supplies the fine-grained GitHub token outside version control.
- MCP authorization and project trust are approved manually in Codex.
- The returned repository data and screenshot are manually reviewed for accuracy, readability, and sensitive information before submission.
- The Filesystem MCP result is checked to confirm that only the intended Homework 5 directory is allowed.
- Atlassian OAuth consent is completed manually for `https://anastasiiabocharnikova.atlassian.net`.
- The Jira screenshot is reviewed to ensure that it contains ticket keys only.
- FastMCP output and the exact 30-word result are verified through automated tests.
- The custom MCP screenshot is manually reviewed for readability and secrets.
