"""
integration/gateways/memory_gateway.py

Adapts existing Memory infrastructure for the Integration Layer.
"""

from __future__ import annotations

from typing import Callable

from integration.exceptions import MemoryIntegrationError


class MemoryGateway:
    """
    Adapts existing Memory infrastructure.

    Purpose:
        Provides controlled access to the existing Memory Service
        (memory.memory_retriever). The Gateway calls the
        infrastructure, handles infrastructure-level exceptions, and
        returns raw infrastructure responses. No translation occurs
        here.

    Owned by:
        integration/gateways/memory_gateway.py

    Consumed by:
        MemoryIntegration.

    Invariants:
        - Never performs translation.
        - Never constructs Domain objects.
        - Never performs business logic.
        - Infrastructure exceptions are caught and translated into
          MemoryIntegrationError.
    """

    def __init__(
        self,
        search_fn: Callable[[str, int], dict[str, list]] = None,
    ) -> None:
        """
        Initialise MemoryGateway.

        Parameters:
            search_fn: Optional search function override. If None,
                the default memory.memory_retriever.retrieve_related_memories
                is used.

        Returns:
            None.

        Raises:
            None.

        Side Effects:
            None.
        """
        if search_fn is None:
            from memory.memory_retriever import retrieve_related_memories as _default_search

            self._search_fn = _default_search
        else:
            self._search_fn = search_fn

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> dict[str, list]:
        """
        Execute memory search through the existing infrastructure.

        Parameters:
            query (str): The search query. Must not be empty.
            top_k (int): Number of memories to retrieve. Default 3.

        Returns:
            dict[str, list]: Raw infrastructure response containing
            keys: "ids", "documents", "distances".

        Raises:
            MemoryIntegrationError: If the infrastructure search fails.

        Side Effects:
            None.
        """
        try:
            return self._search_fn(query, top_k)
        except Exception as exc:
            raise MemoryIntegrationError(
                f"Memory search failed for query: {query!r}"
            ) from exc
