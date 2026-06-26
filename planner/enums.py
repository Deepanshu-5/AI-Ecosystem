"""Planner domain vocabulary.

Defines immutable enums used by the Planner and downstream control-plane
components to express execution intent, complexity, resource requirements,
and model routing guidance.

Owned by: Planner Domain Layer

Consumed by:
  - Planner
  - Information Planner
  - Model Router
  - Context Budgeter

No business logic, serialization, or validation is present in this module.
"""

from enum import Enum


class ExecutionGoal(str, Enum):
    """Represents the planner's final decision about the primary execution domain
    required to answer the user's query.

    Owned by: Planner

    Consumed by:
      - Information Planner
      - Model Router
      - Context Budgeter
    """
    GENERAL = "general"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    SESSION = "session"
    DOCUMENT = "document"
    CODE = "code"


class ExecutionComplexity(str, Enum):
    """Estimated execution effort for a query or plan step.

    Owned by: Planner

    Consumed by the Planner to allocate resources and provide
    hints to the model routing layer.
    """
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RequirementLevel(str, Enum):
    """Whether a resource is required for plan execution.

    Owned by: Planner

    Consumed by the Planner when building dependency graphs and
    validating that prerequisite resources are available.
    """
    NONE = "none"
    REQUIRED = "required"


class ModelHint(str, Enum):
    """Planner guidance consumed by the Model Router.

    Owned by: Planner

    The planner does not select models.
    It only communicates routing intent.
    """
    NONE = "none"
    SMALL = "small"
    LARGE = "large"
