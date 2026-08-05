# Custom MCP API Reference

## Server

- Name: `Homework 5 Custom MCP Server`
- Codex registration: `custom_lorem`
- Transport: stdio
- Source: `custom-mcp-server/server.py`

## Resource

### `lorem://content{?word_count}`

Reads words from `custom-mcp-server/lorem-ipsum.md`.

| Parameter | Type | Required | Default | Validation |
|---|---|---:|---:|---|
| `word_count` | integer | No | `30` | Must be greater than zero and no larger than the source word count |

Examples:

```text
lorem://content
lorem://content?word_count=12
```

The Resource returns `text/plain` containing exactly the requested number of
whitespace-separated words.

## Tool

### `read`

Returns the same word-limited content as the Resource.

Input:

```json
{
  "word_count": 30
}
```

`word_count` is optional and defaults to `30`.

Successful output:

```text
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi
```

Tool annotations declare that `read` is read-only, non-destructive, idempotent,
and closed-world. This allows compatible MCP clients to call it without a write
confirmation.

## Validation errors

For `word_count <= 0`:

```text
word_count must be greater than zero
```

For a value larger than the source:

```text
word_count cannot exceed the <N> available words
```

The server never writes to `lorem-ipsum.md` or any other file.
