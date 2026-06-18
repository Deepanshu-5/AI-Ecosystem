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
    "rag",
    "memory compression",
    "token usage"
]

CONSOLIDATED_PHRASES = [
    "prioritizing long-term memory retention",
    "efficient resource management",
    "system interoperability"
]


def is_project_memory(
    memory: str
) -> bool:

    memory_lower = memory.lower()

    keyword_matches = 0

    for keyword in PROJECT_KEYWORDS:

        if keyword in memory_lower:
            keyword_matches += 1

    return keyword_matches >= 1


def is_consolidated_memory(
    memory: str
) -> bool:

    memory_lower = memory.lower()

    for phrase in CONSOLIDATED_PHRASES:

        if phrase in memory_lower:
            return True

    return False


def find_project_memories():

    data = get_all_memories()

    ids = data["ids"]
    documents = data["documents"]

    project_ids = []
    project_memories = []

    consolidated_ids = []
    consolidated_memories = []

    for memory_id, memory in zip(
        ids,
        documents
    ):

        if is_consolidated_memory(
            memory
        ):

            consolidated_ids.append(
                memory_id
            )

            consolidated_memories.append(
                memory
            )

            continue

        if is_project_memory(
            memory
        ):

            project_ids.append(
                memory_id
            )

            project_memories.append(
                memory
            )

    return {
        "project_ids": project_ids,
        "project_memories": project_memories,
        "consolidated_ids": consolidated_ids,
        "consolidated_memories": consolidated_memories
    }


if __name__ == "__main__":

    result = find_project_memories()

    print(
        f"\nProject Memories: {len(result['project_memories'])}"
    )

    print(
        f"Consolidated Memories: {len(result['consolidated_memories'])}\n"
    )

    print("=== PROJECT MEMORIES ===\n")

    for i, memory in enumerate(
        result["project_memories"],
        start=1
    ):

        print(f"[{i}]")
        print(memory)
        print()

    print("\n=== CONSOLIDATED MEMORIES ===\n")

    for i, memory in enumerate(
        result["consolidated_memories"],
        start=1
    ):

        print(f"[{i}]")
        print(memory)
        print()