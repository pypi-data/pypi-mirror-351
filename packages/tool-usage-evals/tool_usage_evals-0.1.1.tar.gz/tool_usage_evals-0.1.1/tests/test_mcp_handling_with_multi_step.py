"""Test integration of MCP handling with multi-step evaluation"""

import json
import pytest
import os
from tool_usage_evals.multi_step import run_agent_turn, AgentTurnResult
from tool_usage_evals.mcp_handling import (
    mcp_session_context_manager,
    extract_tool_definitions,
    build_mcp_tool_caller,
)
from openai import AzureOpenAI


@pytest.mark.asyncio
async def test_mcp_with_multi_step(aoai_client: AzureOpenAI) -> None:
    """Test using MCP tools with multi-step agent evaluation"""
    async with mcp_session_context_manager(
        "python", [os.path.join(os.path.dirname(__file__), "sample_mcp", "sample_mcp.py")]
    ) as session:
        # Extract tool definitions from MCP session
        tools = await extract_tool_definitions(session)

        # Build MCP tool caller function
        call_tool_fn = await build_mcp_tool_caller(session)

        # Run agent turn with MCP tools
        result = await run_agent_turn(
            aoai_client=aoai_client,
            tools=tools,
            call_tool_fn=call_tool_fn,
            user_message="Say hello to Alice first, and then after that tell me what time it is",
            max_steps=5,
        )

        assert isinstance(result, AgentTurnResult)
        assert len(result.messages) >= 1  # At least user message
        assert result.steps == 2
        assert len(result.tool_calls) >= 1  # Should call at least one tool

        # Check that MCP tools were available and potentially called
        tool_call_names = [t.name for t in result.tool_calls]
        available_tools = ["hello", "get_time"]
        assert any(tool_name in available_tools for tool_name in tool_call_names)


@pytest.mark.asyncio
async def test_mcp_with_multi_step_2(aoai_client: AzureOpenAI) -> None:
    """Test using MCP tools with multi-step agent evaluation"""
    async with mcp_session_context_manager(
        "python", [os.path.join(os.path.dirname(__file__), "sample_mcp", "sample_mcp.py")]
    ) as session:
        # Extract tool definitions from MCP session
        tools = await extract_tool_definitions(session)

        # Build MCP tool caller function
        call_tool_fn = await build_mcp_tool_caller(session)

        # Run agent turn with MCP tools
        result = await run_agent_turn(
            aoai_client=aoai_client,
            tools=tools,
            call_tool_fn=call_tool_fn,
            user_message="What are the models in the catalog?",
            max_steps=5,
        )

        # Check that MCP tools were available and potentially called
        tool_call_names = [t.name for t in result.tool_calls]
        assert "list_models_from_model_catalog" in tool_call_names
