from memory.memory_store import (
    search_memory
)


def retrieve_related_memories(
    query: str,
    top_k: int = 10
):

    return search_memory(
        query=query,
        top_k=top_k
    )