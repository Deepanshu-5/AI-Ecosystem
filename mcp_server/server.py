import sys
from pathlib import Path
root = str(Path(__file__).resolve().parent.parent)

if root not in sys.path:
    sys.path.insert(0, root)

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent  # ← add this
from mcp_server.tools.search_knowledge import search_knowledge

mcp = FastMCP("KnowledgeBase")
from mcp.types import TextContent  # ← add this
@mcp.tool()
def search(question: str):
    result = search_knowledge(question)
    return [TextContent(type="text", text=result)]  # ← wrap in TextContent

if __name__ == "__main__":
    mcp.run()