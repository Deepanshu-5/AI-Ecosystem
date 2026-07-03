"""
budgeting/budget_metadata.py

Immutable metadata recording budgeting facts.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BudgetMetadata:
    """
    Immutable metadata recording token allocation and truncation facts.

    Purpose:
        Captures the complete budgeting state for observability,
        validation, and debugging. Contains only budgeting facts —
        no Planner, Router, provider, model, or cost decisions.

    Owned by:
        budgeting/budget_metadata.py

    Invariants:
        - All token counts are non-negative integers.
        - query_truncated is a boolean.
        - truncated_unit_count is a non-negative integer.
    """

    total_budget: int
    reserved_tokens: int
    query_tokens: int
    context_budget: int
    used_context_tokens: int
    remaining_tokens: int
    knowledge_tokens: int
    memory_tokens: int
    session_tokens: int
    query_truncated: bool = False
    truncated_unit_count: int = 0

    def to_dict(self) -> dict[str, object]:
        """
        Return a stable, explicit dictionary representation.

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
            "total_budget": self.total_budget,
            "reserved_tokens": self.reserved_tokens,
            "query_tokens": self.query_tokens,
            "context_budget": self.context_budget,
            "used_context_tokens": self.used_context_tokens,
            "remaining_tokens": self.remaining_tokens,
            "knowledge_tokens": self.knowledge_tokens,
            "memory_tokens": self.memory_tokens,
            "session_tokens": self.session_tokens,
            "query_truncated": self.query_truncated,
            "truncated_unit_count": self.truncated_unit_count,
        }
