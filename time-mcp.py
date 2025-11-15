from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Time")

@mcp.tool()
async def get_time(timezone: str = "local") -> str:
    """Get current time: 'local' (default) or 'UTC'."""
    tz = timezone.strip().lower()
    now = datetime.now(timezone.utc) if tz == "utc" else datetime.now()
    return now.isoformat(sep=" ", timespec="seconds")

#mcp.run(transport="streamable-http")
mcp.run(transport="stdio")
