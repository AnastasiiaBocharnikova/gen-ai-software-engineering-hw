import asyncio
import importlib.util
from pathlib import Path

import pytest
from fastmcp import Client


SERVER_PATH = Path(__file__).parents[1] / "custom-mcp-server" / "server.py"
SPEC = importlib.util.spec_from_file_location("homework5_custom_mcp", SERVER_PATH)
assert SPEC is not None and SPEC.loader is not None
server = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(server)


def word_count(text: str) -> int:
    return len(text.split())


def test_read_words_defaults_to_exactly_30_words() -> None:
    assert word_count(server.read_words()) == 30


def test_read_words_returns_requested_prefix() -> None:
    result = server.read_words(5)

    assert word_count(result) == 5
    assert result == "Lorem ipsum dolor sit amet,"


@pytest.mark.parametrize("invalid_count", [0, -1])
def test_read_words_rejects_non_positive_counts(invalid_count: int) -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        server.read_words(invalid_count)


def test_read_words_rejects_count_larger_than_source() -> None:
    with pytest.raises(ValueError, match="available words"):
        server.read_words(10_000)


def test_source_path_is_independent_of_working_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)

    assert word_count(server.read_words(7)) == 7


def test_tool_and_resource_return_matching_word_limited_content() -> None:
    async def exercise_server() -> None:
        async with Client(server.mcp) as client:
            default_result = await client.call_tool("read", {})
            custom_result = await client.call_tool("read", {"word_count": 12})
            resource_result = await client.read_resource(
                "lorem://content?word_count=12"
            )

        assert word_count(default_result.data) == 30
        assert word_count(custom_result.data) == 12
        assert resource_result[0].text == custom_result.data

    asyncio.run(exercise_server())


def test_read_tool_is_declared_read_only() -> None:
    async def inspect_tool() -> None:
        async with Client(server.mcp) as client:
            tools = await client.list_tools()

        read_tool = next(tool for tool in tools if tool.name == "read")
        assert read_tool.annotations is not None
        assert read_tool.annotations.readOnlyHint is True
        assert read_tool.annotations.destructiveHint is False
        assert read_tool.annotations.idempotentHint is True
        assert read_tool.annotations.openWorldHint is False

    asyncio.run(inspect_tool())
