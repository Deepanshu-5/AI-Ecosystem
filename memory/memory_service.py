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

    results = recall_with_scores(
    content,
    top_k=5
)

    distances = results["distances"]

    if distances:

        best_distance = min(distances)

        print(
    f"[MEMORY] Closest Distance: {best_distance}",
    file=sys.stderr
)

        if best_distance < 0.25:
            return False

    save_memory(content)

    return True


def recall_with_scores(query, top_k=3):
    return search_memory(query, top_k)

def recall(query, top_k=3):
    results = search_memory(query, top_k)

    documents = results.get("documents", [])

    if documents and isinstance(documents[0], list):
        return documents[0]

    return documents
