"""
retriever/retrieved_context.py

The immutable public contract of the Retrieval subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass

from retriever.knowledge_context import KnowledgeContext
from retriever.memory_context import MemoryContext
from retriever.retrieval_metadata import RetrievalMetadata
from retriever.session_context import SessionContext

CURRENT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class RetrievedContext:
    """
    Represents every piece of information retrieved for downstream
    processing.

    Purpose:
        The single, immutable public contract exposed by the Retrieval
        subsystem. RetrievedContext is the only object that crosses the
        Retriever boundary into downstream components (Context Budgeter,
        Prompt Builder, Observability).

    Owned by:
        retriever/retrieved_context.py

    Consumed by:
        Context Budgeter, Prompt Builder, Observability (future).

    Invariants:
        - Immutable once constructed; retrieved information never
          changes after this point in the pipeline.
        - Contains exactly these five fields — no prompts, no model
          selections, no planner internals, no runtime state.
        - version identifies the schema of this object for backward-
          compatible evolution; it is unrelated to the project's own
          semantic release version (see CHANGELOG.md).
        - KnowledgeContext contains knowledge only; MemoryContext
          contains memory only; SessionContext contains session only.
        - RetrievalMetadata is informational only and must never
          influence downstream behavior.
    """

    knowledge: KnowledgeContext
    memory: MemoryContext
    session: SessionContext
    metadata: RetrievalMetadata
    version: int = CURRENT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """
        Return a stable, explicit, versioned dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, object]: Mapping with fixed key order:
            knowledge, memory, session, metadata, version. Nested
            domain objects are recursively converted to their own stable
            representations.

        Raises:
            None.

        Side Effects:
            None.
        """
        return {
            "knowledge": self.knowledge.to_dict(),
            "memory": self.memory.to_dict(),
            "session": self.session.to_dict(),
            "metadata": self.metadata.to_dict(),
            "version": self.version,
        }
