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

    results = recall(
        content,
        top_k=5
    )

    distances = results["distances"]

    if distances:

        best_distance = min(distances)
        print(f"[MEMORY] Closest Distance: {best_distance}")

        if best_distance < 0.10:
            return False

    save_memory(content)

    return True


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
    "User is building an AI ecosystem using MCP and ChromaDB."
)

    remember(
    "User is building an AI ecosystem using MCP and ChromaDB."
)

    remember(
    "The project uses MCP, ChromaDB, and an AI ecosystem architecture."
)

    print(
        recall(
            "project goal",
            top_k=10
        )
    )