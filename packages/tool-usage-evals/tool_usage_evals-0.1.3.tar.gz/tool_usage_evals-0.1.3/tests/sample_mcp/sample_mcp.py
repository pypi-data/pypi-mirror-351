"""
Sample MCP server, for testing purposes
"""

from mcp.server.fastmcp import Context
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


@mcp.tool()
async def list_models_from_model_catalog(
    ctx: Context, search_for_free_playground: bool = False, publisher_name: str = "", license_name: str = ""
) -> str:
    return "placeholder"


if __name__ == "__main__":
    mcp.run()
