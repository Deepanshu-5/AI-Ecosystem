"""
integration/translators/knowledge_translator.py

Translates between Knowledge infrastructure objects and Domain objects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from retriever.knowledge_context import KnowledgeItem

if TYPE_CHECKING:
    from retrieval.retriever import Document


class KnowledgeTranslator:
    """
    Translates between Knowledge infrastructure objects and Domain
    objects.

    Purpose:
        Converts raw infrastructure Document objects (from the
        KnowledgeGateway) into immutable KnowledgeItem domain
        objects. Translation is deterministic and lossless where
        possible.

    Owned by:
        integration/translators/knowledge_translator.py

    Consumed by:
        KnowledgeIntegration.

    Invariants:
        - Never accesses infrastructure.
        - Never coordinates workflows.
        - Never performs business logic.
        - Translation is deterministic: the same Document always
          produces the same KnowledgeItem.
    """

    def to_domain(self, doc: "Document") -> KnowledgeItem:
        """
        Convert an infrastructure Document into a Domain KnowledgeItem.

        Parameters:
            doc (Document): Raw infrastructure document. Must have
                "text" (str), "metadata" (dict), and "score" (float)
                attributes.

        Returns:
            KnowledgeItem: Immutable domain knowledge item.

        Raises:
            None. Invalid documents are handled defensively.

        Side Effects:
            None.
        """
        source = "Unknown"
        if doc.metadata and isinstance(doc.metadata, dict):
            source = doc.metadata.get("source", "Unknown")

        score: float | None = doc.score if doc.score != 0.0 else None

        return KnowledgeItem(
            text=doc.text,
            source=source,
            score=score,
        )
