from memory.consolidation_retriever import (
    retrieve_project_cluster
)

from memory.consolidator import (
    consolidate_memories
)
from memory.memory_store import get_all_memories


def build_consolidation_plan():

    results = retrieve_project_cluster()

    memories = results["documents"]

    summary = consolidate_memories(
        memories
    )

    return {
        "summary": summary,
        "source_count": len(memories)
    }
    
def should_consolidate(
    threshold: int = 5
):

    data = get_all_memories()

    count = len(
        data["documents"]
    )

    return count >= threshold