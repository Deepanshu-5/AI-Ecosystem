import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

from memory.memory_store import (
    get_all_memories
)


PROJECT_KEYWORDS = [
    "ai ecosystem",
    "chromadb",
    "mcp",
    "rag",
    "memory compression",
    "ollama",
    "qwen",
    "token usage"
]


def classify_memory(
    memory: str
):

    memory_lower = memory.lower()

    for keyword in PROJECT_KEYWORDS:

        if keyword in memory_lower:
            return "PROJECT"

    return "OTHER"


def analyze_memories():

    data = get_all_memories()

    ids = data["ids"]
    documents = data["documents"]

    print(
        f"\nTotal Memories: {len(documents)}\n"
    )

    for index, (memory_id, memory) in enumerate(
        zip(ids, documents),
        start=1
    ):

        category = classify_memory(
            memory
        )

        print("=" * 80)

        print(
            f"Memory #{index}"
        )

        print(
            f"ID: {memory_id}"
        )

        print(
            f"Category: {category}"
        )

        print(
            f"Content:\n{memory}"
        )

        print()


if __name__ == "__main__":

    analyze_memories()