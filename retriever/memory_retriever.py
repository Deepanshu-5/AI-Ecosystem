"""
retriever/memory_retriever.py

Implements persistent user memory retrieval from the Memory Layer.
"""

from __future__ import annotations

from typing import Callable

from retriever.memory_context import MemoryContext, MemoryEntry


class MemoryRetriever:
    """
    Retrieves persistent user memory from the Memory Layer.

    Purpose:
        Queries memory storage and returns relevant user memories as
        an immutable MemoryContext. MemoryRetriever owns memory
        retrieval only — it never accesses document storage, session
        history, or performs planning.

    Owned by:
        retriever/memory_retriever.py

    Consumed by:
        RetrievalBuilder.

    Invariants:
        - Never accesses document storage.
        - Never accesses session history.
        - Never performs planning.
        - Never budgets tokens.
        - Domain layer remains independent from infrastructure; the
          actual search function is injected at construction.
    """

    def __init__(
        self,
        search_fn: Callable[[str], list[MemoryEntry]],
    ) -> None:
        """
        Initialise MemoryRetriever with an infrastructure search
        function.

        Parameters:
            search_fn (Callable[[str], list[MemoryEntry]]):
                A function that accepts a query string and returns a
                list of MemoryEntries. This function is provided by the
                infrastructure layer and must be deterministic.

        Returns:
            None.

        Raises:
            None.

        Side Effects:
            None.
        """
        self._search_fn = search_fn

    def retrieve(self, query: str) -> MemoryContext:
        """
        Retrieve persistent user memory for the given query.

        Parameters:
            query (str): The search query derived from the original user
                query. Must not be empty or whitespace-only.

        Returns:
            MemoryContext: Immutable context containing all retrieved
            memory entries and metadata.

        Raises:
            None. Empty retrieval is valid and returns an empty
            MemoryContext.

        Side Effects:
            None. The search function may access infrastructure, but
            MemoryRetriever itself performs no side effects.
        """
        entries = self._search_fn(query)
        return MemoryContext(
            entries=tuple(entries),
            metadata={
                "query": query,
                "entry_count": len(entries),
            },
        )
