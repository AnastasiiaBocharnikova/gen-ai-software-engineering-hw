# How to Run Homework 5

Run all commands from the `homework-5/` directory.

## Prerequisites

- Python 3.11 or newer
- Codex CLI or Codex app
- Node.js and `npx` for the Filesystem MCP server
- Existing GitHub and Jira credentials configured as described in `README.md`

## Install the custom server

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r custom-mcp-server/requirements.txt
```

If the local Python executable has another supported name, use it instead of
`python3.11`. FastMCP requires Python 3.10 or newer; Python 3.11+ is recommended
for this homework.

## Start the server directly

```bash
.venv/bin/python custom-mcp-server/server.py
```

The server uses the MCP stdio transport. It waits for an MCP client on standard
input, so no web page or listening port appears. Press `Ctrl+C` to stop it.

## Connect Codex

The project-scoped configuration is already stored in `.codex/config.toml`:

```toml
[mcp_servers.custom_lorem]
command = ".venv/bin/python"
args = ["custom-mcp-server/server.py"]
cwd = "."
enabled_tools = ["read"]
default_tools_approval_mode = "writes"
required = true
```

Verify it from `homework-5/`:

```bash
codex mcp list
codex mcp get custom_lorem
```

Start Codex from the same directory so relative paths resolve correctly:

```bash
codex
```

## Security policy

Use `.codex/config.toml` as the runtime configuration for Codex. It contains
the task-specific tool allowlists. The portable `mcp.json` records the four
server registrations but cannot express all Codex-specific restrictions, so
other MCP clients must configure equivalent read-only allowlists themselves.

Atlassian's OAuth consent advertises Read, Search, and Write scopes for its
shared hosted server. This homework exposes only resource discovery and JQL
search tools through the local Jira allowlist.

## Use the Resource

Resources are read-only URIs that expose content from sources such as files or
APIs. This server provides a parameterized lorem ipsum Resource:

```text
lorem://content
lorem://content?word_count=12
```

The omitted `word_count` defaults to `30`.

## Use the `read` Tool

Tools are actions an AI client can call. Ask Codex:

```text
Using only the custom_lorem MCP server, call the read tool with word_count set
to 30. Return the tool result and state the exact number of returned words. Do
not modify any files.
```

The `read` tool accepts an optional positive integer `word_count` and returns
exactly that many words. It reports an error if the value is below one or
larger than the available source text.

## Run tests and coverage

```bash
.venv/bin/python -m pytest tests/test_custom_mcp_server.py -v
.venv/bin/python -m pytest \
  --cov=custom-mcp-server \
  --cov-report=term-missing \
  --cov-fail-under=85
```

The tests cover default and custom limits, validation, working-directory
independence, Resource reads, and Tool calls.

## Troubleshooting

- `No module named fastmcp`: install `custom-mcp-server/requirements.txt` in
  `homework-5/.venv`.
- `custom_lorem` is missing: start Codex from `homework-5/` and restart it after
  editing `.codex/config.toml`.
- Source-file error: confirm `custom-mcp-server/lorem-ipsum.md` exists next to
  `server.py`.
- Invalid `word_count`: use a positive value no larger than the number of words
  in `lorem-ipsum.md`.
