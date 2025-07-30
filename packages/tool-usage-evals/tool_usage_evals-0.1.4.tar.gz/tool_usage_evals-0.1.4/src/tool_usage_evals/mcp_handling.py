"""
Utils for handling tools that live inside MCP servers
"""

from typing import AsyncIterator, Awaitable, Callable, AsyncContextManager
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult


@asynccontextmanager
async def mcp_session_context_manager(command: str, args: list[str]) -> AsyncIterator[ClientSession]:
    """
    Async context manager that yields an MCP session.
    Example arguments:
        command="python"
        args=["./mcp.py"]
    """
    server_params = StdioServerParameters(
        command=command,
        args=args,
    )

    async with stdio_client(server_params) as (stdio, write):
        async with ClientSession(stdio, write) as session:
            await session.initialize()
            yield session


async def extract_tool_definitions(session: ClientSession) -> list[dict]:
    """Extracts the tool definitions object (ingestable by openai chat completion)  from the MCP client session"""
    mcp_tools = (await session.list_tools()).tools

    openai_tools = []
    for mcp_tool in mcp_tools:
        # Ensure the parameters schema has additionalProperties: false; otherwise OpenAI will throw error
        parameters = mcp_tool.inputSchema.copy() if mcp_tool.inputSchema else {"type": "object", "properties": {}}
        if "additionalProperties" not in parameters:
            parameters["additionalProperties"] = False

        openai_tools.append(
            {
                "type": "function",
                "name": mcp_tool.name,
                "description": mcp_tool.description,
                "parameters": parameters,
                "strict": False,
            }
        )

    return openai_tools


async def build_mcp_tool_caller(session: ClientSession) -> Callable[..., Awaitable[CallToolResult]]:
    """Returns a call_tool function, which will call the tool functions from the specified mcp session"""

    async def call_mcp_tool_fn(name: str, args: dict) -> CallToolResult:
        response = await session.call_tool(name=name, arguments=args)
        return response

    return call_mcp_tool_fn
