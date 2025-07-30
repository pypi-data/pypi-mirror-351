"""
Evaluate tool usage on a LM sequence that comprises potentially multiple tool calls
"""

import json
from openai.types.responses import ResponseFunctionToolCall
from typing import Any, Awaitable, Callable, Union
from openai import AzureOpenAI
from pydantic import BaseModel, Field


class AgentTurnResult(BaseModel):
    """Result of running a multi-step agent turn"""

    messages: list[Union[dict, ResponseFunctionToolCall]] = Field(
        description="Complete conversation history including user, assistant, and function messages"
    )
    tool_calls: list[ResponseFunctionToolCall] = Field(description="All function calls made during the turn")
    final_response: Any = Field(description="Final response from the model or error message")
    steps: int = Field(description="Number of steps taken in the conversation")


async def run_agent_turn(
    aoai_client: AzureOpenAI,
    model: str,
    tools: list[dict],
    call_tool_fn: Callable[..., Awaitable],
    user_message: str,
    max_steps: int = 10,
) -> AgentTurnResult:
    """
    Given the LLM client, tool definitions, and tool functions, run a full agent turn using the LLM (e.g. could be
    multiple steps within single turn).
    Specifically, the turn is comprised of 1 or more steps, where if a step requires a tool call, the tool function will
    be called and response returned back to the LLM , looping like this until it reaches a step with no more tool calls.
    """
    messages = [{"role": "user", "content": user_message}]
    all_tool_calls = []

    for step in range(max_steps):
        response = aoai_client.responses.create(model=model, input=messages, tools=tools)

        # Check if response contains function calls
        has_function_calls = any(item.type == "function_call" for item in response.output)

        if not has_function_calls:
            # No more function calls, return final response
            return AgentTurnResult(
                messages=messages,
                tool_calls=all_tool_calls,
                final_response=response.output_text if hasattr(response, "output_text") else response.output,
                steps=step + 1,
            )

        # Process function calls
        function_calls = [item for item in response.output if item.type == "function_call"]

        # Add function calls to messages
        for func_call in function_calls:
            messages.append(func_call)
            all_tool_calls.append(func_call)

        # Execute functions and add results
        for func_call in function_calls:
            try:
                name = func_call.name
                args = json.loads(func_call.arguments)
                result = await call_tool_fn(name, args)

                messages.append({"type": "function_call_output", "call_id": func_call.call_id, "output": str(result)})
            except Exception as e:
                messages.append(
                    {"type": "function_call_output", "call_id": func_call.call_id, "output": f"Error: {str(e)}"}
                )

    # If we reach max_steps, return what we have
    return AgentTurnResult(
        messages=messages,
        tool_calls=all_tool_calls,
        final_response="Max steps reached",
        steps=max_steps,
    )
