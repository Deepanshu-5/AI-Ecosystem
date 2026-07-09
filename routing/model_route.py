"""
routing/model_route.py

Immutable canonical output contract for Model Routing.
"""

from dataclasses import dataclass

from routing.model_target import ModelTarget

CURRENT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ModelRoute:
    """
    The immutable routing decision produced by ModelRouter.

    Purpose:
        Captures the selected semantic model capability target and the
        deterministic reason for that selection.

    Owned by:
        routing/model_route.py

    Consumed by:
        Future Model Execution Integration and routing tests.

    Invariants:
        - Immutable once constructed.
        - Contains exactly target, reason, and version.
        - target is a valid ModelTarget.
        - reason is deterministic, non-empty text.
        - version is a supported ModelRoute schema version.
        - Contains no provider, model name, prompt, execution plan, or
          runtime execution settings.
    """

    target: ModelTarget
    reason: str
    version: int = CURRENT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """
        Return a stable, explicit, versioned dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, object]: Mapping with fixed key order: target,
            reason, version. The target is serialized using enum value.

        Raises:
            None.

        Side Effects:
            None.
        """
        return {
            "target": self.target.value,
            "reason": self.reason,
            "version": self.version,
        }
