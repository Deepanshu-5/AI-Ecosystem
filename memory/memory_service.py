import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

from memory.memory_store import (
    save_memory,
    search_memory
)


def remember(
    content: str
):

    existing = recall(
    content,
    top_k=5
)

    if content not in existing:
     save_memory(content)


def recall(
    query: str,
    top_k: int = 3
):

    return search_memory(
        query,
        top_k
    )
if __name__ == "__main__":

    remember(
        "PROJECT_GOAL: Build an AI ecosystem that reduces token usage through RAG, memory compression, MCP integration, vector databases, and local LLMs."
    )

    remember(
        "User integrated Claude Desktop MCP successfully."
    )

    print(
        recall(
            "project goal",
            top_k=10
        )
    )