"""
retriever/knowledge_context.py

Domain object representing factual information retrieved from the
Knowledge Layer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeItem:
    """
    A single piece of retrieved factual knowledge.

    Purpose:
        Represents one document chunk, fact, or knowledge entry
        retrieved from the Knowledge Layer, along with its source
        and optional relevance score.

    Owned by:
        retriever/knowledge_context.py

    Consumed by:
        KnowledgeContext, KnowledgeRetriever, RetrievalBuilder.

    Invariants:
        - text is a non-empty string representing the retrieved
          knowledge content.
        - source identifies the origin of the knowledge (e.g., file
          name, collection name, URL).
        - score is optional and represents a retrieval relevance score
          if available.
    """

    text: str
    source: str
    score: float | None = None

    def to_dict(self) -> dict[str, object]:
        """
        Return a stable, explicit dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, object]: Mapping with fixed key order: text,
            source, score.

        Raises:
            None.

        Side Effects:
            None.
        """
        return {
            "text": self.text,
            "source": self.source,
            "score": self.score,
        }


@dataclass(frozen=True)
class KnowledgeContext:
    """
    Represents all factual knowledge retrieved for a single query.

    Purpose:
        Aggregates KnowledgeItems retrieved from the Knowledge Layer
        into a single immutable context object for downstream
        consumption by the Context Budgeter.

    Owned by:
        retriever/knowledge_context.py

    Consumed by:
        RetrievedContext, RetrievalBuilder, RetrievalValidator.

    Invariants:
        - Contains only KnowledgeItems; no memory entries, no session
          messages, no planner internals.
        - items is an immutable tuple; never a mutable list.
        - metadata is informational only and never influences
          retrieval behavior.
    """

    items: tuple[KnowledgeItem, ...]
    metadata: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        """
        Return a stable, explicit dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, object]: Mapping with fixed key order: items,
            metadata. Items are serialized recursively.

        Raises:
            None.

        Side Effects:
            None.
        """
        return {
            "items": [item.to_dict() for item in self.items],
            "metadata": dict(self.metadata),
        }
