import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)
    
from memory.consolidation_retriever import (
    retrieve_project_cluster
)

from memory.consolidator import (
    consolidate_memories
)
from memory.memory_store import get_all_memories
from memory.memory_store import (
    save_memory,
    delete_memories
)

def build_consolidation_plan():

    results = retrieve_project_cluster()

    ids = results["ids"]
    memories = results["documents"]

    summary = consolidate_memories(
    memories
)
    if not summary.strip():
     return {
         "summary": "",
        "source_count": 0
    }
    save_memory(summary)

    delete_memories(ids)

    return {
    "summary": summary,
    "source_count": len(memories)
}
    
def should_consolidate(
    threshold: int = 999999
):

    data = get_all_memories()

    count = len(
        data["documents"]
    )

    return count >= threshold
if __name__ == "__main__":
    build_consolidation_plan()
    print(get_all_memories())
    data = get_all_memories()

    print(
    "Memory Count:",
    len(data["documents"])
)
   