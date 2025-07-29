"""
Sample MCP server, for testing purposes
"""

import time
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sample-mcp")


@mcp.tool()
async def hello(name: str) -> str:
    """Returns a greeting to the user"""
    return f"Hello {name}!"


@mcp.tool()
async def get_time() -> str:
    """Gets the current time as a unix timestamp"""
    return str(int(time.time()))


if __name__ == "__main__":
    mcp.run()
