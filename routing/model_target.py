"""
routing/model_target.py

Semantic model capability targets selected by Model Routing.
"""

from enum import Enum, unique


@unique
class ModelTarget(Enum):
    """
    Represents the semantic model capability target required by a plan.

    Purpose:
        Communicates expected model capability without naming providers,
        concrete model identifiers, runtime placement, or infrastructure.

    Owned by:
        routing/model_target.py

    Consumed by:
        ModelRoute and future Model Execution Integration.

    Invariants:
        - A target is exactly one of LIGHTWEIGHT, STANDARD, ADVANCED.
        - Values are stable semantic identifiers.
        - Contains no routing behavior or infrastructure mapping.
    """

    LIGHTWEIGHT = "lightweight"
    STANDARD = "standard"
    ADVANCED = "advanced"
