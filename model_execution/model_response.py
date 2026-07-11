"""
Immutable canonical output contract for Model Execution Integration.

Implementation justification:
    This new module is required by the frozen Model Execution Integration
    architecture. It owns only the stable response contract and does not
    take ownership of runtime invocation or infrastructure behavior.
"""

from __future__ import annotations

from dataclasses import dataclass

CURRENT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ModelResponse:
    """
    The immutable canonical response from model execution.

    Purpose:
        Represents the stable textual output returned after runtime execution.

    Owned by:
        model_execution/model_response.py

    Consumed by:
        Model Execution Integration callers.

    Invariants:
        - Immutable once constructed.
        - Contains only response content and schema version.
        - Serialization has a stable key order.
        - Contains no provider or operational metadata.
    """

    content: str
    version: int = CURRENT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """Return a stable, versioned dictionary representation."""
        return {
            "content": self.content,
            "version": self.version,
        }
