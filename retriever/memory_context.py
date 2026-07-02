"""
retriever/memory_context.py

Domain object representing persistent user memory retrieved from the
Memory Layer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryEntry:
    """
    A single piece of retrieved persistent user memory.

    Purpose:
        Represents one memory entry retrieved from the Memory Layer,
        along with its identifier and optional relevance score.

    Owned by:
        retriever/memory_context.py

    Consumed by:
        MemoryContext, MemoryRetriever, RetrievalBuilder.

    Invariants:
        - content is a non-empty string representing the memory
          content.
        - memory_id is an optional identifier from the Memory Layer.
        - score is optional and represents a retrieval relevance score
          if available.
    """

    content: str
    memory_id: str | None = None
    score: float | None = None

    def to_dict(self) -> dict[str, object]:
        """
        Return a stable, explicit dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, object]: Mapping with fixed key order: content,
            memory_id, score.

        Raises:
            None.

        Side Effects:
            None.
        """
        return {
            "content": self.content,
            "memory_id": self.memory_id,
            "score": self.score,
        }


@dataclass(frozen=True)
class MemoryContext:
    """
    Represents all persistent user memory retrieved for a single query.

    Purpose:
        Aggregates MemoryEntries retrieved from the Memory Layer into
        a single immutable context object for downstream consumption
        by the Context Budgeter.

    Owned by:
        retriever/memory_context.py

    Consumed by:
        RetrievedContext, RetrievalBuilder, RetrievalValidator.

    Invariants:
        - Contains only MemoryEntries; no knowledge items, no session
          messages, no documents.
        - entries is an immutable tuple; never a mutable list.
        - metadata is informational only and never influences
          retrieval behavior.
    """

    entries: tuple[MemoryEntry, ...]
    metadata: dict[str, object]
    
    @classmethod
    def empty(cls) -> "MemoryContext":
        return cls(
            entries=(),
            metadata={},
        )

    def to_dict(self) -> dict[str, object]:
        """
        Return a stable, explicit dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, object]: Mapping with fixed key order: entries,
            metadata. Entries are serialized recursively.

        Raises:
            None.

        Side Effects:
            None.
        """
        return {
            "entries": [entry.to_dict() for entry in self.entries],
            "metadata": dict(self.metadata),
        }
