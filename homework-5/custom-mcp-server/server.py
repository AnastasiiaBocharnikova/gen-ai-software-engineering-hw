"""Custom FastMCP server for word-limited lorem ipsum content."""

from pathlib import Path

from fastmcp import FastMCP


SOURCE_FILE = Path(__file__).with_name("lorem-ipsum.md")


def read_words(word_count: int = 30) -> str:
    """Return exactly ``word_count`` words from the lorem ipsum source."""
    if word_count < 1:
        raise ValueError("word_count must be greater than zero")

    words = SOURCE_FILE.read_text(encoding="utf-8").split()
    if word_count > len(words):
        raise ValueError(
            f"word_count cannot exceed the {len(words)} available words"
        )

    return " ".join(words[:word_count])


mcp = FastMCP("Homework 5 Custom MCP Server")


@mcp.resource(
    "lorem://content{?word_count}",
    mime_type="text/plain",
)
def lorem_resource(word_count: int = 30) -> str:
    """Read a configurable number of words through an MCP resource URI."""
    return read_words(word_count)


@mcp.tool(
    name="read",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def read(word_count: int = 30) -> str:
    """Return the requested number of words from the lorem ipsum resource."""
    return read_words(word_count)


if __name__ == "__main__":
    mcp.run()
