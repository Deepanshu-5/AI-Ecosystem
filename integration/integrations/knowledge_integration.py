"""
integration/integrations/knowledge_integration.py

Coordinates knowledge retrieval through the Integration Layer.
"""

from __future__ import annotations

from integration.gateways.knowledge_gateway import KnowledgeGateway
from integration.translators.knowledge_translator import KnowledgeTranslator
from retriever.knowledge_context import KnowledgeItem


class KnowledgeIntegration:
    """
    Coordinates knowledge retrieval through the Integration Layer.

    Purpose:
        Orchestrates the knowledge retrieval workflow: invokes the
        KnowledgeGateway to access infrastructure, then invokes the
        KnowledgeTranslator to convert infrastructure objects into
        Domain KnowledgeItems. Returns the Domain objects upstream.

    Owned by:
        integration/integrations/knowledge_integration.py

    Consumed by:
        RetrieverIntegration.

    Invariants:
        - Never accesses infrastructure directly.
        - Never performs translation itself.
        - Never coordinates memory or session retrieval.
        - Owns knowledge workflow only.
    """

    def __init__(
        self,
        gateway: KnowledgeGateway | None = None,
        translator: KnowledgeTranslator | None = None,
    ) -> None:
        """
        Initialise KnowledgeIntegration.

        Parameters:
            gateway (KnowledgeGateway | None): Gateway for
                infrastructure communication. If None, a default
                KnowledgeGateway is constructed.
            translator (KnowledgeTranslator | None): Translator for
                object conversion. If None, a default
                KnowledgeTranslator is constructed.

        Returns:
            None.

        Raises:
            None.

        Side Effects:
            None.
        """
        self._gateway = gateway if gateway is not None else KnowledgeGateway()
        self._translator = translator if translator is not None else KnowledgeTranslator()

    def search(
        self,
        query: str,
        top_k: int = 5,
        final_k: int = 3,
    ) -> list[KnowledgeItem]:
        """
        Retrieve knowledge through the Integration Layer.

        Parameters:
            query (str): The search query.
            top_k (int): Number of documents to retrieve initially.
                Default 5.
            final_k (int): Number of documents to return after
                reranking. Default 3.

        Returns:
            list[KnowledgeItem]: Immutable domain knowledge items.

        Raises:
            KnowledgeIntegrationError: Propagated from the Gateway or
                Translator if an infrastructure failure occurs.

        Side Effects:
            None. The Gateway may trigger cache reads/writes in the
            underlying infrastructure.
        """
        docs = self._gateway.search(query, top_k=top_k, final_k=final_k)
        return [self._translator.to_domain(doc) for doc in docs]
