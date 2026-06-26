import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

from mcp.server.fastmcp import FastMCP
from memory.memory_service import recall

mcp = FastMCP("KnowledgeBase")

@mcp.tool()
def ping() -> str:
    return "pong"


@mcp.tool()
def recall_memory(
    query: str
) -> str:

    memories = recall(query)

    return "\n".join(memories)

from memory.memory_service import remember

@mcp.tool()
def remember_memory(
    content: str
) -> str:

    remember(content)

    return "Memory stored successfully."

from conversation_memory.session_memory import (
    process_message
)

@mcp.tool()
def record_response(
    session_id: str,
    response: str
) -> str:

    process_message(
        session_id,
        "assistant",
        response
    )

    return "Response recorded."
from mcp_server.tools.search_knowledge import (
    search_knowledge
)

@mcp.tool()
def search(
    question: str,
    session_id: str = ""
) -> str:

    return search_knowledge(
        question,
        session_id=session_id
    )

if __name__ == "__main__":
    mcp.run()