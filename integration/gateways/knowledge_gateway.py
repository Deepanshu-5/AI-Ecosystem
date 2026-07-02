"""
integration/gateways/knowledge_gateway.py

Adapts existing Knowledge infrastructure for the Integration Layer.
"""

from __future__ import annotations

from typing import Callable

from integration.exceptions import KnowledgeIntegrationError


class KnowledgeGateway:
    """
    Adapts existing Knowledge infrastructure.

    Purpose:
        Provides controlled access to the existing Knowledge Service
        (services.knowledge_service). The Gateway calls the
        infrastructure, handles infrastructure-level exceptions, and
        returns raw infrastructure objects. No translation occurs
        here.

    Owned by:
        integration/gateways/knowledge_gateway.py

    Consumed by:
        KnowledgeIntegration.

    Invariants:
        - Never performs translation.
        - Never constructs Domain objects.
        - Never performs business logic.
        - Infrastructure exceptions are caught and translated into
          KnowledgeIntegrationError.
    """

    def __init__(
        self,
        search_fn: Callable[[str, int, int], list] = None,
    ) -> None:
        """
        Initialise KnowledgeGateway.

        Parameters:
            search_fn: Optional search function override. If None,
                the default services.knowledge_service.search is used.

        Returns:
            None.

        Raises:
            None.

        Side Effects:
            None.
        """
        if search_fn is None:
            from services.knowledge_service import search as _default_search

            self._search_fn = _default_search
        else:
            self._search_fn = search_fn

    def search(
        self,
        query: str,
        top_k: int = 5,
        final_k: int = 3,
    ) -> list:
        """
        Execute knowledge search through the existing infrastructure.

        Parameters:
            query (str): The search query. Must not be empty.
            top_k (int): Number of documents to retrieve initially.
                Default 5.
            final_k (int): Number of documents to return after
                reranking. Default 3.

        Returns:
            list: Raw infrastructure document objects.

        Raises:
            KnowledgeIntegrationError: If the infrastructure search
                fails for any reason.

        Side Effects:
            May trigger cache reads/writes in the underlying
            knowledge_service.
        """
        try:
            return self._search_fn(query, top_k, final_k)
        except Exception as exc:
            raise KnowledgeIntegrationError(
                f"Knowledge search failed for query: {query!r}"
            ) from exc
