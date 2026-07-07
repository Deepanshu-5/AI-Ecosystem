"""
retriever/retrieval_metadata.py

Domain object containing deterministic diagnostic information about a
retrieval operation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalMetadata:
    """
    Provides deterministic diagnostic information about a retrieval
    operation.

    Purpose:
        Captures timing and count information for observability,
        performance analysis, and debugging. RetrievalMetadata is
        informational only — downstream systems must never change
        execution behavior based on its contents.

    Owned by:
        retriever/retrieval_metadata.py

    Consumed by:
        RetrievedContext, RetrievalBuilder, Observability (future).

    Invariants:
        - All counts are non-negative integers.
        - All latency values are non-negative integers in milliseconds.
        - Downstream systems must never branch logic based on these
          values.
    """

    knowledge_count: int
    memory_count: int
    session_count: int
    knowledge_latency_ms: int
    memory_latency_ms: int
    session_latency_ms: int
    total_latency_ms: int

    def to_dict(self) -> dict[str, object]:
        """
        Return a stable, explicit dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, object]: Mapping with fixed key order matching
            field declaration order.

        Raises:
            None.

        Side Effects:
            None.
        """
        return {
            "knowledge_count": self.knowledge_count,
            "memory_count": self.memory_count,
            "session_count": self.session_count,
            "knowledge_latency_ms": self.knowledge_latency_ms,
            "memory_latency_ms": self.memory_latency_ms,
            "session_latency_ms": self.session_latency_ms,
            "total_latency_ms": self.total_latency_ms,
        }
