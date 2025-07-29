"""Unit tests for single turn evals"""

from tool_usage_evals.single_step import evaluate_tool_name_was_selected
from openai import AzureOpenAI


def test_evaluate_matching_tool_name(aoai_client: AzureOpenAI) -> None:
    tools = [
        {
            "type": "function",
            "name": "get_current_time",
            "description": "Get the current time in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g. San Francisco",
                    },
                },
                "required": ["location"],
                "additionalProperties": False,
            },
            "strict": True,
        }
    ]
    result = evaluate_tool_name_was_selected(
        aoai_client=aoai_client,
        tools=tools,
        user_message="What is the current time in New York?",
        expected_tool_names="get_current_time",
        n_trials=3,
    )
    assert result.accuracy == 1.0
    assert result.n_trials == 3
