"""
Evaluate tool selection on a single LLM step
"""

from openai import AzureOpenAI
import os
from pydantic import BaseModel, Field
import openai
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


class MatchingToolNameResult(BaseModel):
    accuracy: float = Field(description="Accuracy of matching correct tool names")
    n_trials: int


def evaluate_tool_name_was_selected(
    aoai_client: AzureOpenAI,
    tools: list[dict],
    user_message: str,
    expected_tool_names: str,
    n_trials: int = 1,
    use_retry: bool = True,
) -> MatchingToolNameResult:
    """
    Given model + tools and initial user message, take a single LLM step , checking if the selected tool calls contains
    the expected tool name or not.
    Will do n trials to gather statistics.
    """
    n_successes = 0
    for i in range(n_trials):
        input_messages = [{"role": "user", "content": user_message}]

        create_response_fn = aoai_client.responses.create
        if use_retry:
            create_response_fn = retry_decorator(aoai_client.responses.create)

        response = create_response_fn(
            model=os.environ["AOAI_MODEL"],
            input=input_messages,
            tools=tools,
            tool_choice="auto",
        )

        # Check for tool calls in response.output
        tool_calls = [item for item in response.output if item.type == "function_call"]
        selected_tool_names = [tool_call.name for tool_call in tool_calls]
        success = expected_tool_names in selected_tool_names
        if success:
            n_successes += 1

    return MatchingToolNameResult(
        accuracy=n_successes / n_trials,
        n_trials=n_trials,
    )
