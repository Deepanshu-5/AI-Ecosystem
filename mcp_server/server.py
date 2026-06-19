import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from mcp_server.tools.search_knowledge import (
    search_knowledge
)
from memory.memory_service import (
    remember,
    recall
)
from conversation_memory.session_memory import (
    process_message
)

mcp = FastMCP(
    "KnowledgeBase"
)


@mcp.tool()
def search(
    question: str,
    session_id: str = ""
):
    """Search knowledge base with optional session context.

    Pass session_id to include the conversation summary and recent
    messages for this session. Use the same session_id for every turn
    in one conversation (e.g. "ai-ecosystem-001").

    After answering, call record_response with the same session_id.
    """

    result = search_knowledge(
        question,
        session_id=session_id
    )

    return [
        TextContent(
            type="text",
            text=result
        )
    ]


@mcp.tool()
def record_response(
    session_id: str,
    response: str
):
    """Record the assistant response for session memory.

    Call after answering when using session_id with search.
    """

    process_message(
        session_id,
        "assistant",
        response
    )

    return [
        TextContent(
            type="text",
            text="Response recorded."
        )
    ]


@mcp.tool()
def remember_memory(
    content: str
):

    remember(
        content
    )

    return [
        TextContent(
            type="text",
            text="Memory stored successfully."
        )
    ]


@mcp.tool()
def recall_memory(
    query: str
):

    memories = recall(
        query
    )

    return [
        TextContent(
            type="text",
            text="\n".join(
                memories
            )
        )
    ]


if __name__ == "__main__":
    mcp.run()
