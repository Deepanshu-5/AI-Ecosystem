"""
integration/integrations/memory_integration.py

Coordinates memory retrieval through the Integration Layer.
"""

from __future__ import annotations

from integration.gateways.memory_gateway import MemoryGateway
from integration.translators.memory_translator import MemoryTranslator
from retriever.memory_context import MemoryEntry


class MemoryIntegration:
    """
    Coordinates memory retrieval through the Integration Layer.

    Purpose:
        Orchestrates the memory retrieval workflow: invokes the
        MemoryGateway to access infrastructure, then invokes the
        MemoryTranslator to convert infrastructure responses into
        Domain MemoryEntries. Returns the Domain objects upstream.

    Owned by:
        integration/integrations/memory_integration.py

    Consumed by:
        RetrieverIntegration.

    Invariants:
        - Never accesses infrastructure directly.
        - Never performs translation itself.
        - Never coordinates knowledge or session retrieval.
        - Owns memory workflow only.
    """

    def __init__(
        self,
        gateway: MemoryGateway | None = None,
        translator: MemoryTranslator | None = None,
    ) -> None:
        """
        Initialise MemoryIntegration.

        Parameters:
            gateway (MemoryGateway | None): Gateway for
                infrastructure communication. If None, a default
                MemoryGateway is constructed.
            translator (MemoryTranslator | None): Translator for
                object conversion. If None, a default
                MemoryTranslator is constructed.

        Returns:
            None.

        Raises:
            None.

        Side Effects:
            None.
        """
        self._gateway = gateway if gateway is not None else MemoryGateway()
        self._translator = translator if translator is not None else MemoryTranslator()

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[MemoryEntry]:
        """
        Retrieve memory through the Integration Layer.

        Parameters:
            query (str): The search query.
            top_k (int): Number of memories to retrieve. Default 3.

        Returns:
            list[MemoryEntry]: Immutable domain memory entries.

        Raises:
            MemoryIntegrationError: Propagated from the Gateway or
                Translator if an infrastructure failure occurs.

        Side Effects:
            None.
        """
        results = self._gateway.search(query, top_k=top_k)
        return self._translator.to_domain(results)
