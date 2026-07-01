"""
planner/planner_builder.py

Assembles an already-decided set of planning components into a
validated, immutable ExecutionPlan.
"""

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.execution_plan import ExecutionPlan
from planner.planner_validator import PlannerValidator
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements


class PlannerBuilder:
    """
    Assembles a validated ExecutionPlan from already-decided planning
    components.

    Purpose:
        Provides the single, explicit construction path for
        ExecutionPlan: assemble the four decided components into the
        immutable contract, validate the result, and return it. The
        builder does not decide processing_goal, complexity, or
        resource_requirements itself — those decisions are made
        upstream and passed in already finalized.

    Owned by:
        planner/planner_builder.py

    Consumed by:
        QueryAnalyzer (future).

    Invariants:
        - Never infers, defaults, or repairs a missing or invalid
          component value; an invalid input is reported via
          PlannerValidationError, never silently corrected.
        - Never mutates an already-built ExecutionPlan.
        - Always validates before returning; an unvalidated
          ExecutionPlan is never returned to a caller.
    """

    @staticmethod
    def build(
        processing_goal: ProcessingGoal,
        complexity: Complexity,
        resource_requirements: ResourceRequirements,
        decision_trace: DecisionTrace,
    ) -> ExecutionPlan:
        """
        Assemble and validate an ExecutionPlan.

        Parameters:
            processing_goal (ProcessingGoal): The decided processing
                goal. Not inferred here — must already be decided by
                the caller.
            complexity (Complexity): The decided complexity estimate.
            resource_requirements (ResourceRequirements): The decided
                resource requirements.
            decision_trace (DecisionTrace): The human-readable
                explanation for the three decisions above.

        Returns:
            ExecutionPlan: A validated, immutable execution plan at the
            current schema version.

        Raises:
            PlannerValidationError: If the assembled plan fails
                structural, logical, or semantic validation. Propagated
                from PlannerValidator unchanged — never caught, wrapped,
                or silently repaired here.

        Side Effects:
            None.
        """
        plan = ExecutionPlan(
            processing_goal=processing_goal,
            complexity=complexity,
            resource_requirements=resource_requirements,
            decision_trace=decision_trace,
        )
        PlannerValidator.validate(plan)
        return plan