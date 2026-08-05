# Homework 5: MCP Servers

**Author:** Anastasiia Bocharnikova

## Overview

This assignment configures four MCP servers for Codex. Tasks 1–3 connect Codex to GitHub, a restricted local filesystem directory, and Jira. Task 4 implements a custom FastMCP server that returns an exact number of words from a local Markdown resource.

## Task 1: GitHub MCP

The GitHub integration uses GitHub's hosted Streamable HTTP endpoint. The functional, project-scoped Codex configuration is stored in `.codex/config.toml`. The sanitized `mcp.json` mirrors the same server registration for the assignment deliverable; Codex itself reads the TOML configuration.

### Prerequisites

- Codex CLI or Codex app
- A GitHub fine-grained personal access token with read access to the target repository
- The token exported as `GITHUB_PAT_TOKEN`

Use the minimum repository permissions needed for the demonstration. Do not save the token in this repository or include it in screenshots.

### Configure authentication

Export the token in the shell before starting Codex:

```bash
export GITHUB_PAT_TOKEN="your-fine-grained-token"
cd homework-5
codex
```

For the Codex desktop app, make `GITHUB_PAT_TOKEN` available to the app process before starting the app. Restart Codex after changing MCP configuration or its environment.

### Verify the server

From `homework-5/`, run:

```bash
codex mcp list
codex mcp get github
```

In Codex, use `/mcp` and confirm that `github` is connected without an authentication or startup error.

### Demonstration request

```text
Using only the GitHub MCP server, list the five most recent pull requests
for AnastasiiaBocharnikova/gen-ai-software-engineering-hw. For each one,
show its number, title, state, author, and URL. Then briefly summarize the
most recent pull request. Do not create or modify anything.
```

The server is configured with GitHub's `X-MCP-Readonly` header. Codex also prompts for MCP tools that are not marked read-only.

### Evidence

The successful request and response are captured at:

```text
docs/screenshots/terminal.png
```

An additional Codex workflow screenshot is available at:

```text
docs/screenshots/codex_1.png
```

## Task 2: Filesystem MCP

The Filesystem integration uses the official `@modelcontextprotocol/server-filesystem` package. It is pinned to version `2026.7.10` and receives `.` as its only allowed directory. Start Codex from `homework-5/` so that the server cannot access sibling homework folders or the rest of the home directory.

Codex loads only the tools required by this task:

- `list_allowed_directories`
- `list_directory`
- `directory_tree`
- `read_text_file`

Write, edit, move, and delete tools are not enabled.

### Prerequisites

- Node.js and `npx`
- Codex CLI or Codex app
- Network access during the first start so `npx` can download the pinned package

### Start and verify

```bash
cd homework-5
codex mcp list
codex mcp get filesystem
codex
```

In Codex, use `/mcp` and confirm that `filesystem` is connected. The first start may take longer while `npx` installs the package in its local cache.

### Demonstration request

```text
Using only the Filesystem MCP server:

1. Show the allowed directories.
2. List the files and directories in the allowed Homework 5 directory.
3. Read TASKS.md and summarize the requirements of Task 2.
Do not create, edit, move, or delete anything.
```

### Evidence

The successful Filesystem MCP request and response are captured at:

```text
docs/screenshots/filesystem-mcp-result.png
```

## Task 3: Jira MCP

The Jira integration uses Atlassian's official hosted Rovo MCP server with OAuth 2.1. OAuth credentials are stored by Codex outside this repository. The committed configuration contains no Jira password, token, or session credential.

The integration targets:

- Jira site: `https://anastasiiabocharnikova.atlassian.net`
- Project key: `SCRUM`
- Issue type: `Bug`

Only the tools needed to discover the accessible Jira site and run a read-only JQL query are enabled:

- `getAccessibleAtlassianResources`
- `searchJiraIssuesUsingJql`

### Authenticate and verify

From `homework-5/`, run:

```bash
codex mcp login jira
codex mcp list
codex mcp get jira
```

Complete Atlassian's browser consent flow and authorize access only to the intended Jira Cloud site. In Codex, use `/mcp` and confirm that `jira` is connected.

### Demonstration request

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

### Evidence and privacy

The successful request and response are captured at:

```text
docs/screenshots/jira-mcp-result.png
```

The OAuth consent screen for the selected Jira site is captured at:

```text
docs/screenshots/jira-oauth-consent.png
```

The screenshot must show the request, completed Jira MCP calls, and five ticket keys. It must not expose OAuth tokens, ticket summaries, descriptions, user information, or comments.

## Task 4: Custom FastMCP Server

The custom Python server in `custom-mcp-server/server.py` uses FastMCP 3.4.4
and the local stdio transport. It reads `lorem-ipsum.md` and exposes the same
word-limited content through two MCP primitives:

- **Resource:** a read-only URI that a client reads from a file, API, or other
  content source. This server provides `lorem://content{?word_count}`.
- **Tool:** an action that a client can call. This server provides
  `read(word_count=30)`.

Both interfaces use one shared `read_words` function and return exactly the
requested number of whitespace-separated words. Counts below one or above the
available source length are rejected with a clear error.

### Tech stack

- Python 3.11 or newer
- FastMCP 3.4.4
- pytest 8.4.2
- pytest-cov 6.2.1
- MCP stdio transport

### Setup, run, and test

Complete installation, startup, MCP connection, usage, testing, coverage, and
troubleshooting instructions are in [`HOWTORUN.md`](HOWTORUN.md).

Quick verification:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r custom-mcp-server/requirements.txt
.venv/bin/python -m pytest --cov=custom-mcp-server --cov-fail-under=85
codex mcp get custom_lorem
```

### Demonstration request

```text
Using only the custom_lorem MCP server, call the read tool with word_count set
to 30. Return the tool result and state the exact number of returned words. Do
not modify any files.
```

The successful request and response must be captured at:

```text
docs/screenshots/custom-mcp-read-tool-result.png
```

## Project structure

```text
homework-5/
├── .codex/config.toml
├── HOWTORUN.md
├── mcp.json
├── README.md
├── TASKS.md
├── custom-mcp-server/
│   ├── lorem-ipsum.md
│   ├── requirements.txt
│   └── server.py
├── tests/
│   └── test_custom_mcp_server.py
└── docs/
    ├── AI_USAGE.md
    └── screenshots/
        ├── codex_1.png
        ├── custom-mcp-read-tool-result.png
        ├── filesystem-mcp-result.png
        ├── jira-mcp-result.png
        ├── jira-oauth-consent.png
        └── terminal.png
```

The local `.venv`, pytest cache, coverage files, and other generated artifacts
are intentionally excluded from version control.
