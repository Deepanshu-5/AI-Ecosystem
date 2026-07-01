"""
planner/execution_plan.py

Domain object representing the Planner's immutable, final output.
"""

from dataclasses import dataclass

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements

CURRENT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ExecutionPlan:
    """
    The Planner's immutable, final decision output.

    Purpose:
        Represents everything downstream components (Context Budgeter,
        Prompt Builder, Model Router, Tool Router, Execution Layer) need
        to know about what the Planner decided for a single query —
        nothing more. ExecutionPlan is a decision, not an action.

    Owned by:
        planner/execution_plan.py

    Consumed by:
        Context Budgeter, Prompt Builder, Model Router, Tool Router,
        Execution Layer, Observability.

    Invariants:
        - Immutable once constructed; planner decisions never change
          after this point in the pipeline.
        - Contains exactly these five fields — no retrieved data, no
          prompt text, no runtime state, no models, no tools, no results.
        - `version` identifies the schema of this object for backward-
          compatible evolution; it is unrelated to the project's own
          semantic release version (see CHANGELOG.md).
    """

    processing_goal: ProcessingGoal
    complexity: Complexity
    resource_requirements: ResourceRequirements
    decision_trace: DecisionTrace
    version: int = CURRENT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """
        Return a stable, explicit, versioned dictionary representation.

        Parameters:
            None.

        Returns:
            dict[str, object]: Mapping with fixed key order:
            processing_goal, complexity, resource_requirements,
            decision_trace, version. Nested domain objects are
            recursively converted to their own stable representations.

        Raises:
            None.

        Side Effects:
            None.
        """
        return {
            "processing_goal": self.processing_goal.value,
            "complexity": self.complexity.value,
            "resource_requirements": self.resource_requirements.to_dict(),
            "decision_trace": self.decision_trace.to_dict(),
            "version": self.version,
        }