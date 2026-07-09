"""
routing/model_routing_validator.py

Internal validation for Model Routing boundary and output invariants.
"""

from planner.complexity import Complexity
from planner.execution_plan import (
    CURRENT_SCHEMA_VERSION as EXECUTION_PLAN_SCHEMA_VERSION,
)
from planner.execution_plan import ExecutionPlan
from planner.processing_goal import ProcessingGoal

from routing.exceptions import ModelRoutingValidationError
from routing.model_route import (
    CURRENT_SCHEMA_VERSION as MODEL_ROUTE_SCHEMA_VERSION,
)
from routing.model_route import ModelRoute
from routing.model_target import ModelTarget

_KNOWN_EXECUTION_PLAN_VERSIONS = frozenset({EXECUTION_PLAN_SCHEMA_VERSION})
_KNOWN_MODEL_ROUTE_VERSIONS = frozenset({MODEL_ROUTE_SCHEMA_VERSION})

_EXPECTED_TARGET_BY_COMPLEXITY = {
    Complexity.LOW: ModelTarget.LIGHTWEIGHT,
    Complexity.MEDIUM: ModelTarget.STANDARD,
    Complexity.HIGH: ModelTarget.ADVANCED,
}


class ModelRoutingValidator:
    """
    Internal validator for Model Routing contracts.

    Purpose:
        Validates only Model Routing boundary assumptions, ModelRoute
        output invariants, and the complexity-to-target routing invariant.

    Owned by:
        routing/model_routing_validator.py

    Consumed by:
        ModelRouter and routing tests.

    Invariants:
        - Performs no Planner semantic validation.
        - Performs no retrieval, prompt construction, configuration,
          infrastructure access, provider lookup, or model execution.
        - Never mutates the objects it inspects.
        - Reports invalid state explicitly and never repairs it.
    """

    @staticmethod
    def validate_input(execution_plan: ExecutionPlan) -> None:
        """
        Validate the Model Routing input boundary.

        Parameters:
            execution_plan (ExecutionPlan): Candidate Planner output.

        Returns:
            None. Absence of an exception means the input is routable.

        Raises:
            ModelRoutingValidationError: If the value is not an
            ExecutionPlan, has an unsupported schema version, or contains
            invalid complexity or processing goal values.

        Side Effects:
            None.
        """
        violations: list[str] = []

        if not isinstance(execution_plan, ExecutionPlan):
            violations.append(
                f"root: expected ExecutionPlan, got "
                f"{type(execution_plan).__name__}"
            )
        else:
            if not isinstance(execution_plan.version, int):
                violations.append(
                    f"version: expected int, got "
                    f"{type(execution_plan.version).__name__}"
                )
            elif execution_plan.version not in _KNOWN_EXECUTION_PLAN_VERSIONS:
                violations.append(
                    f"version: {execution_plan.version} is not supported "
                    f"for Model Routing"
                )

            if not isinstance(execution_plan.complexity, Complexity):
                violations.append(
                    f"complexity: expected Complexity, got "
                    f"{type(execution_plan.complexity).__name__}"
                )

            if not isinstance(execution_plan.processing_goal, ProcessingGoal):
                violations.append(
                    f"processing_goal: expected ProcessingGoal, got "
                    f"{type(execution_plan.processing_goal).__name__}"
                )

        if violations:
            raise ModelRoutingValidationError(
                "Model Routing input failed validation:\n- "
                + "\n- ".join(violations)
            )

    @staticmethod
    def validate_output(model_route: ModelRoute) -> None:
        """
        Validate the ModelRoute output contract.

        Parameters:
            model_route (ModelRoute): Candidate routing output.

        Returns:
            None. Absence of an exception means the output is valid.

        Raises:
            ModelRoutingValidationError: If output structure, reason,
            target, or schema version is invalid.

        Side Effects:
            None.
        """
        violations: list[str] = []

        if not isinstance(model_route, ModelRoute):
            violations.append(
                f"root: expected ModelRoute, got {type(model_route).__name__}"
            )
        else:
            if not isinstance(model_route.target, ModelTarget):
                violations.append(
                    f"target: expected ModelTarget, got "
                    f"{type(model_route.target).__name__}"
                )

            if not isinstance(model_route.reason, str):
                violations.append(
                    f"reason: expected str, got "
                    f"{type(model_route.reason).__name__}"
                )
            elif not model_route.reason.strip():
                violations.append("reason: must not be empty or whitespace-only")

            if not isinstance(model_route.version, int):
                violations.append(
                    f"version: expected int, got "
                    f"{type(model_route.version).__name__}"
                )
            elif model_route.version not in _KNOWN_MODEL_ROUTE_VERSIONS:
                violations.append(
                    f"version: {model_route.version} is not supported "
                    f"for Model Routing"
                )

        if violations:
            raise ModelRoutingValidationError(
                "ModelRoute failed validation:\n- " + "\n- ".join(violations)
            )

    @staticmethod
    def validate_routing_invariant(
        execution_plan: ExecutionPlan,
        model_route: ModelRoute,
    ) -> None:
        """
        Validate exact consistency between complexity and routed target.

        Parameters:
            execution_plan (ExecutionPlan): Validated routing input.
            model_route (ModelRoute): Validated routing output.

        Returns:
            None. Absence of an exception means the invariant holds.

        Raises:
            ModelRoutingValidationError: If complexity does not map to
            the exact V1 target.

        Side Effects:
            None.
        """
        ModelRoutingValidator.validate_input(execution_plan)
        ModelRoutingValidator.validate_output(model_route)

        expected_target = _EXPECTED_TARGET_BY_COMPLEXITY[execution_plan.complexity]

        if model_route.target is not expected_target:
            raise ModelRoutingValidationError(
                "Model Routing invariant failed validation:\n- "
                f"complexity {execution_plan.complexity.value!r} must route "
                f"to target {expected_target.value!r}, got "
                f"{model_route.target.value!r}"
            )
