"""
retriever/knowledge_retriever.py

Implements factual knowledge retrieval from the Knowledge Layer.
"""

from __future__ import annotations

from typing import Callable

from retriever.knowledge_context import KnowledgeContext, KnowledgeItem


class KnowledgeRetriever:
    """
    Retrieves factual knowledge from the Knowledge Layer.

    Purpose:
        Queries knowledge storage and returns matching documents as
        an immutable KnowledgeContext. KnowledgeRetriever owns knowledge
        retrieval only — it never retrieves memory, session history, or
        performs budgeting.

    Owned by:
        retriever/knowledge_retriever.py

    Consumed by:
        RetrievalBuilder.

    Invariants:
        - Never retrieves memory.
        - Never retrieves session history.
        - Never budgets context.
        - Never determines relevance policy.
        - Never modifies retrieved documents.
        - Domain layer remains independent from infrastructure; the
          actual search function is injected at construction.
    """

    def __init__(
        self,
        search_fn: Callable[[str], list[KnowledgeItem]],
    ) -> None:
        """
        Initialise KnowledgeRetriever with an infrastructure search
        function.

        Parameters:
            search_fn (Callable[[str], list[KnowledgeItem]]):
                A function that accepts a query string and returns a
                list of KnowledgeItems. This function is provided by the
                infrastructure layer and must be deterministic.

        Returns:
            None.

        Raises:
            None.

        Side Effects:
            None.
        """
        self._search_fn = search_fn

    def retrieve(self, query: str) -> KnowledgeContext:
        """
        Retrieve factual knowledge for the given query.

        Parameters:
            query (str): The search query derived from the original user
                query. Must not be empty or whitespace-only.

        Returns:
            KnowledgeContext: Immutable context containing all retrieved
            knowledge items and metadata.

        Raises:
            None. Empty retrieval is valid and returns an empty
            KnowledgeContext.

        Side Effects:
            None. The search function may access infrastructure, but
            KnowledgeRetriever itself performs no side effects.
        """
        items = self._search_fn(query)
        return KnowledgeContext(
            items=tuple(items),
            metadata={
                "query": query,
                "item_count": len(items),
            },
        )
