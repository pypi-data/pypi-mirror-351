"""Unit tests for mcp_handling module"""

import pytest
import os
from tool_usage_evals.mcp_handling import (
    mcp_session_context_manager,
    extract_tool_definitions,
    build_mcp_tool_caller,
)


@pytest.mark.asyncio
async def test_mcp_session_generator():
    """Test that mcp_session_generator yields a working session"""
    async with mcp_session_context_manager(
        "python", [os.path.join(os.path.dirname(__file__), "sample_mcp", "sample_mcp.py")]
    ) as session:
        # Test that we can list tools from the session
        response = await session.list_tools()
        assert len(response.tools) == 3


@pytest.mark.asyncio
async def test_extract_tool_definitions():
    """Test extracting tool definitions from MCP session"""
    async with mcp_session_context_manager(
        "python", [os.path.join(os.path.dirname(__file__), "sample_mcp", "sample_mcp.py")]
    ) as session:
        tools = await extract_tool_definitions(session)

        assert len(tools) == 3
        assert all(tool["type"] == "function" for tool in tools)
        assert any(tool["name"] == "hello" for tool in tools)
        assert any(tool["name"] == "get_time" for tool in tools)
        assert all("description" in tool for tool in tools)
        assert all("parameters" in tool for tool in tools)


@pytest.mark.asyncio
async def test_build_mcp_tool_caller():
    """Test building and using MCP tool caller function"""
    async with mcp_session_context_manager(
        "python", [os.path.join(os.path.dirname(__file__), "sample_mcp", "sample_mcp.py")]
    ) as session:
        call_tool_fn = await build_mcp_tool_caller(session)

        # Test calling the hello tool
        result = await call_tool_fn("hello", {"name": "World"})
        assert "Hello World!" in str(result)

        # Test calling the get_time tool
        result = await call_tool_fn("get_time", {})
        # Should return a timestamp string
        assert result.content[0].type == "text"
