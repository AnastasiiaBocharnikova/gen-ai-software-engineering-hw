# Homework 5: MCP Servers

**Author:** Anastasiia Bocharnikova

## Overview

This assignment configures external MCP servers for Codex and implements a custom FastMCP server. Tasks 1–3 connect Codex to GitHub, a restricted local filesystem directory, and Jira.

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

## Project structure

```text
homework-5/
├── .codex/config.toml
├── mcp.json
├── README.md
├── TASKS.md
└── docs/
    ├── AI_USAGE.md
    └── screenshots/
        ├── codex_1.png
        ├── filesystem-mcp-result.png
        ├── jira-mcp-result.png
        ├── jira-oauth-consent.png
        └── terminal.png
```

The custom-server code, setup instructions, tests, and remaining screenshots will be added in Task 4.
