"""
budgeting/budgeted_context.py

The immutable public contract of the Context Budgeting Layer.
"""

from __future__ import annotations

from dataclasses import dataclass

from budgeting.budget_metadata import BudgetMetadata
from retriever.knowledge_context import KnowledgeContext
from retriever.memory_context import MemoryContext
from retriever.session_context import SessionContext

CURRENT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class BudgetedContext:
    """
    Represents retrieved context after token budgeting.

    Purpose:
        The single, immutable public contract exposed by the Budgeting
        Layer. BudgetedContext is the only object that crosses the
        Budgeter boundary into downstream components (Prompt Builder,
        Observability).

    Owned by:
        budgeting/budgeted_context.py

    Invariants:
        - Immutable once constructed.
        - Contains exactly these fields — no prompts, no model
          selections, no planner internals, no runtime state.
        - version identifies the schema for backward-compatible
          evolution.
        - Metadata records budgeting facts only.
    """

    knowledge: KnowledgeContext
    memory: MemoryContext
    session: SessionContext
    metadata: BudgetMetadata
    effective_query: str
    version: int = CURRENT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """
        Return a stable, explicit, versioned dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, object]: Mapping with fixed key order.

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
            "effective_query": self.effective_query,
            "version": self.version,
        }
