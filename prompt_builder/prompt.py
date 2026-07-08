"""
prompt_builder/prompt.py

Immutable Prompt domain contract.
"""

from __future__ import annotations

from dataclasses import dataclass

CURRENT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Prompt:
    """
    The Prompt Builder's immutable, final output.

    Purpose:
        Represents the deterministic model-ready textual prompt assembled
        from BudgetedContext.
    """

    content: str
    version: int = CURRENT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """
        Return a stable, explicit, versioned dictionary representation.

        Returns:
            dict[str, object]: Mapping with fixed key order: content, version.
        """
        return {
            "content": self.content,
            "version": self.version,
        }
