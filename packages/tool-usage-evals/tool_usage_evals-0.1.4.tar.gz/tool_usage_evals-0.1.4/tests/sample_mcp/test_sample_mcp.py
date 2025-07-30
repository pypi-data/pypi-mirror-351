"""
Quick test to ensure the sample MCP is working
"""

import pytest
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
async def test_sample_mcp_list_tools():
    server_params = StdioServerParameters(
        command="python",
        args=[os.path.join(os.path.dirname(__file__), "sample_mcp.py")],
    )

    async with stdio_client(server_params) as (stdio, write):
        async with ClientSession(stdio, write) as session:
            await session.initialize()
            response = await session.list_tools()
            tools = response.tools
            assert len(tools) == 3
            print(tools)
