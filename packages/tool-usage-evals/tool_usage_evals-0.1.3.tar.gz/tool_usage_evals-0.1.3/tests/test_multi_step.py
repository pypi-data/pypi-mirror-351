"""Unit tests for multi-step evals"""

import os
from dotenv import load_dotenv
import openai
import pytest
from tool_usage_evals.multi_step import run_agent_turn, AgentTurnResult
from openai import AzureOpenAI
from tenacity import (
    retry,
    wait_random_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)


retry_decorator = retry(
    retry=retry_if_exception_type(openai.RateLimitError),
    wait=wait_random_exponential(min=10, max=90),
    stop=stop_after_attempt(6),
    reraise=True,
)

load_dotenv()


def get_time(location: str) -> str:
    """Gives current time at a location"""
    return "It's noontime, 12pm."


def get_temperature(location: str) -> str:
    """Get temperature for a location"""
    return "It's 56 degrees Fahrenheit."


async def call_function(name: str, args: dict) -> str:
    """Simple function dispatcher for tests"""
    if name == "get_time":
        return get_time(**args)
    elif name == "get_temperature":
        return get_temperature(**args)
    else:
        raise ValueError(f"Unknown function: {name}")


@pytest.mark.asyncio
async def test_run_agent_turn_with_function_call(aoai_client: AzureOpenAI) -> None:
    tools = [
        {
            "type": "function",
            "name": "get_time",
            "description": "Gives current time at a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g. Paris",
                    },
                },
                "required": ["location"],
                "additionalProperties": False,
            },
            "strict": True,
        },
        {
            "type": "function",
            "name": "get_temperature",
            "description": "Get temperature for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g. Paris",
                    },
                },
                "required": ["location"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    ]

    result = await retry_decorator(run_agent_turn)(
        aoai_client=aoai_client,
        model=os.environ["AOAI_MODEL"],
        tools=tools,
        call_tool_fn=call_function,
        user_message="Find the time in paris, and if it's daytime, then find the temperature.",
        max_steps=5,
    )

    assert isinstance(result, AgentTurnResult)
    assert len(result.messages) >= 1  # At least user message
    assert result.steps >= 2
    assert len(result.tool_calls) == 2

    # check tool call names
    tool_call_names = [t.name for t in result.tool_calls]
    assert "get_time" in tool_call_names
    assert "get_temperature" in tool_call_names
