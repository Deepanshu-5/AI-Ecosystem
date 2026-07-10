"""
routing/tool_routing_validator.py

Internal validation for Tool Routing boundary and output invariants.
"""

from planner.execution_plan import (
    CURRENT_SCHEMA_VERSION as EXECUTION_PLAN_SCHEMA_VERSION,
)
from planner.execution_plan import ExecutionPlan
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements

from routing.exceptions import ToolRoutingValidationError
from routing.tool_capability import ToolCapability
from routing.tool_route import (
    CURRENT_SCHEMA_VERSION as TOOL_ROUTE_SCHEMA_VERSION,
)
from routing.tool_route import ToolRoute

_KNOWN_EXECUTION_PLAN_VERSIONS = frozenset({EXECUTION_PLAN_SCHEMA_VERSION})
_KNOWN_TOOL_ROUTE_VERSIONS = frozenset({TOOL_ROUTE_SCHEMA_VERSION})

_CANONICAL_CAPABILITY_ORDER = (
    ToolCapability.KNOWLEDGE_ACCESS,
    ToolCapability.MEMORY_ACCESS,
    ToolCapability.SESSION_ACCESS,
)

_REASON_BY_CAPABILITIES = {
    (): "no resource access capabilities required",
    (
        ToolCapability.SESSION_ACCESS,
    ): "session requirement routes to session access capability",
    (
        ToolCapability.MEMORY_ACCESS,
    ): "memory requirement routes to memory access capability",
    (
        ToolCapability.MEMORY_ACCESS,
        ToolCapability.SESSION_ACCESS,
    ): "memory and session requirements route to memory and session access capabilities",
    (
        ToolCapability.KNOWLEDGE_ACCESS,
    ): "knowledge requirement routes to knowledge access capability",
    (
        ToolCapability.KNOWLEDGE_ACCESS,
        ToolCapability.SESSION_ACCESS,
    ): "knowledge and session requirements route to knowledge and session access capabilities",
    (
        ToolCapability.KNOWLEDGE_ACCESS,
        ToolCapability.MEMORY_ACCESS,
    ): "knowledge and memory requirements route to knowledge and memory access capabilities",
    (
        ToolCapability.KNOWLEDGE_ACCESS,
        ToolCapability.MEMORY_ACCESS,
        ToolCapability.SESSION_ACCESS,
    ): (
        "knowledge, memory, and session requirements route to knowledge, "
        "memory, and session access capabilities"
    ),
}


class ToolRoutingValidator:
    """
    Internal validator for Tool Routing contracts.

    Purpose:
        Validates only Tool Routing boundary assumptions, ToolRoute
        output invariants, and resource-requirement-to-capability
        routing invariants.

    Owned by:
        routing/tool_routing_validator.py

    Consumed by:
        ToolRouter and routing tests.

    Invariants:
        - Performs no Planner heuristic validation.
        - Performs no retrieval, prompt construction, configuration,
          infrastructure access, tool discovery, tool resolution, or
          tool execution.
        - Never mutates the objects it inspects.
        - Reports invalid state explicitly and never repairs it.
    """

    @staticmethod
    def validate_input(execution_plan: ExecutionPlan) -> None:
        """
        Validate the Tool Routing input boundary.

        Parameters:
            execution_plan (ExecutionPlan): Candidate Planner output.

        Returns:
            None. Absence of an exception means the input is routable.

        Raises:
            ToolRoutingValidationError: If the value is not an
            ExecutionPlan, has an unsupported schema version, or contains
            invalid processing goal or resource requirement values.

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
                    f"for Tool Routing"
                )

            if not isinstance(execution_plan.processing_goal, ProcessingGoal):
                violations.append(
                    f"processing_goal: expected ProcessingGoal, got "
                    f"{type(execution_plan.processing_goal).__name__}"
                )

            requirements = execution_plan.resource_requirements
            if not isinstance(requirements, ResourceRequirements):
                violations.append(
                    f"resource_requirements: expected ResourceRequirements, "
                    f"got {type(requirements).__name__}"
                )
            else:
                ToolRoutingValidator._validate_requirement_boolean(
                    violations,
                    "knowledge",
                    requirements.knowledge,
                )
                ToolRoutingValidator._validate_requirement_boolean(
                    violations,
                    "memory",
                    requirements.memory,
                )
                ToolRoutingValidator._validate_requirement_boolean(
                    violations,
                    "session",
                    requirements.session,
                )

        if violations:
            raise ToolRoutingValidationError(
                "Tool Routing input failed validation:\n- "
                + "\n- ".join(violations)
            )

    @staticmethod
    def validate_output(tool_route: ToolRoute) -> None:
        """
        Validate the ToolRoute output contract.

        Parameters:
            tool_route (ToolRoute): Candidate routing output.

        Returns:
            None. Absence of an exception means the output is valid.

        Raises:
            ToolRoutingValidationError: If output structure,
            capabilities, reason, or schema version is invalid.

        Side Effects:
            None.
        """
        violations: list[str] = []

        if not isinstance(tool_route, ToolRoute):
            violations.append(
                f"root: expected ToolRoute, got {type(tool_route).__name__}"
            )
        else:
            capabilities = tool_route.capabilities
            if not isinstance(capabilities, tuple):
                violations.append(
                    f"capabilities: expected tuple, got "
                    f"{type(capabilities).__name__}"
                )
            else:
                ToolRoutingValidator._validate_capability_members(
                    violations,
                    capabilities,
                )
                ToolRoutingValidator._validate_unique_capabilities(
                    violations,
                    capabilities,
                )
                ToolRoutingValidator._validate_canonical_order(
                    violations,
                    capabilities,
                )

            if not isinstance(tool_route.reason, str):
                violations.append(
                    f"reason: expected str, got "
                    f"{type(tool_route.reason).__name__}"
                )
            elif not tool_route.reason.strip():
                violations.append("reason: must not be empty or whitespace-only")

            if not isinstance(tool_route.version, int):
                violations.append(
                    f"version: expected int, got "
                    f"{type(tool_route.version).__name__}"
                )
            elif tool_route.version not in _KNOWN_TOOL_ROUTE_VERSIONS:
                violations.append(
                    f"version: {tool_route.version} is not supported "
                    f"for Tool Routing"
                )

        if violations:
            raise ToolRoutingValidationError(
                "ToolRoute failed validation:\n- " + "\n- ".join(violations)
            )

    @staticmethod
    def validate_routing_invariant(
        execution_plan: ExecutionPlan,
        tool_route: ToolRoute,
    ) -> None:
        """
        Validate exact consistency between requirements and capabilities.

        Parameters:
            execution_plan (ExecutionPlan): Validated routing input.
            tool_route (ToolRoute): Validated routing output.

        Returns:
            None. Absence of an exception means the invariant holds.

        Raises:
            ToolRoutingValidationError: If resource requirements do not
            map exactly to the ToolRoute capabilities and reason.

        Side Effects:
            None.
        """
        ToolRoutingValidator.validate_input(execution_plan)
        ToolRoutingValidator.validate_output(tool_route)

        requirements = execution_plan.resource_requirements
        capabilities = tool_route.capabilities
        violations: list[str] = []

        ToolRoutingValidator._validate_requirement_capability_equivalence(
            violations,
            "knowledge",
            requirements.knowledge,
            ToolCapability.KNOWLEDGE_ACCESS,
            capabilities,
        )
        ToolRoutingValidator._validate_requirement_capability_equivalence(
            violations,
            "memory",
            requirements.memory,
            ToolCapability.MEMORY_ACCESS,
            capabilities,
        )
        ToolRoutingValidator._validate_requirement_capability_equivalence(
            violations,
            "session",
            requirements.session,
            ToolCapability.SESSION_ACCESS,
            capabilities,
        )

        all_requirements_false = (
            not requirements.knowledge
            and not requirements.memory
            and not requirements.session
        )
        if all_requirements_false != (capabilities == ()):
            violations.append(
                "empty route invariant: all requirements false must "
                "correspond exactly to empty capabilities"
            )

        expected_reason = _REASON_BY_CAPABILITIES[capabilities]
        if tool_route.reason != expected_reason:
            violations.append(
                f"reason: expected {expected_reason!r}, got "
                f"{tool_route.reason!r}"
            )

        if violations:
            raise ToolRoutingValidationError(
                "Tool Routing invariant failed validation:\n- "
                + "\n- ".join(violations)
            )

    @staticmethod
    def _validate_requirement_boolean(
        violations: list[str],
        name: str,
        value: object,
    ) -> None:
        if type(value) is not bool:
            violations.append(
                f"resource_requirements.{name}: expected bool, got "
                f"{type(value).__name__}"
            )

    @staticmethod
    def _validate_capability_members(
        violations: list[str],
        capabilities: tuple[object, ...],
    ) -> None:
        for index, capability in enumerate(capabilities):
            if not isinstance(capability, ToolCapability):
                violations.append(
                    f"capabilities[{index}]: expected ToolCapability, got "
                    f"{type(capability).__name__}"
                )

    @staticmethod
    def _validate_unique_capabilities(
        violations: list[str],
        capabilities: tuple[object, ...],
    ) -> None:
        if not all(
            isinstance(capability, ToolCapability)
            for capability in capabilities
        ):
            return

        if len(set(capabilities)) != len(capabilities):
            violations.append("capabilities: duplicate capability is not allowed")

    @staticmethod
    def _validate_canonical_order(
        violations: list[str],
        capabilities: tuple[object, ...],
    ) -> None:
        canonical_positions = {
            capability: index
            for index, capability in enumerate(_CANONICAL_CAPABILITY_ORDER)
        }

        previous_position = -1
        for capability in capabilities:
            if not isinstance(capability, ToolCapability):
                return

            position = canonical_positions[capability]
            if position <= previous_position:
                violations.append(
                    "capabilities: must be in canonical order "
                    "KNOWLEDGE_ACCESS, MEMORY_ACCESS, SESSION_ACCESS"
                )
                return
            previous_position = position

    @staticmethod
    def _validate_requirement_capability_equivalence(
        violations: list[str],
        name: str,
        required: bool,
        capability: ToolCapability,
        capabilities: tuple[ToolCapability, ...],
    ) -> None:
        present = capability in capabilities
        if required != present:
            violations.append(
                f"{name} invariant: requirement {required!r} must "
                f"correspond exactly to {capability.value!r} presence "
                f"{present!r}"
            )
