import pytest

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.execution_plan import ExecutionPlan
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements
from routing.exceptions import ToolRoutingValidationError
from routing.tool_capability import ToolCapability
from routing.tool_route import ToolRoute
from routing.tool_routing_validator import ToolRoutingValidator


def _plan(
    knowledge: bool = False,
    memory: bool = False,
    session: bool = False,
    processing_goal: ProcessingGoal = ProcessingGoal.GENERAL,
) -> ExecutionPlan:
    return ExecutionPlan(
        processing_goal=processing_goal,
        complexity=Complexity.LOW,
        resource_requirements=ResourceRequirements(
            knowledge=knowledge,
            memory=memory,
            session=session,
        ),
        decision_trace=DecisionTrace(
            processing_goal_reason="General query.",
            complexity_reason="Simple lookup.",
            resource_requirements_reason="No retrieval is required.",
        ),
    )


def _route(
    capabilities: tuple[ToolCapability, ...] = (),
    reason: str = "no resource access capabilities required",
) -> ToolRoute:
    return ToolRoute(capabilities=capabilities, reason=reason)


def test_valid_execution_plan_accepted():
    ToolRoutingValidator.validate_input(_plan())


def test_invalid_input_type_rejected():
    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_input("not a plan")


def test_unsupported_execution_plan_version_rejected():
    plan = _plan()
    object.__setattr__(plan, "version", 2)

    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_input(plan)


def test_invalid_processing_goal_rejected():
    plan = _plan()
    object.__setattr__(plan, "processing_goal", "general")

    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_input(plan)


def test_invalid_resource_requirements_rejected():
    plan = _plan()
    object.__setattr__(plan, "resource_requirements", "requirements")

    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_input(plan)


@pytest.mark.parametrize("field", ["knowledge", "memory", "session"])
def test_non_boolean_resource_requirement_rejected(field):
    plan = _plan()
    object.__setattr__(plan.resource_requirements, field, 1)

    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_input(plan)


def test_valid_tool_route_accepted():
    ToolRoutingValidator.validate_output(_route())


def test_invalid_output_type_rejected():
    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_output("not a route")


def test_non_tuple_capabilities_rejected():
    route = _route()
    object.__setattr__(route, "capabilities", [ToolCapability.KNOWLEDGE_ACCESS])

    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_output(route)


def test_invalid_capability_member_rejected():
    route = _route()
    object.__setattr__(route, "capabilities", ("knowledge_access",))

    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_output(route)


def test_duplicate_capability_rejected():
    route = _route()
    object.__setattr__(
        route,
        "capabilities",
        (
            ToolCapability.KNOWLEDGE_ACCESS,
            ToolCapability.KNOWLEDGE_ACCESS,
        ),
    )

    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_output(route)


def test_non_canonical_order_rejected():
    route = _route()
    object.__setattr__(
        route,
        "capabilities",
        (
            ToolCapability.SESSION_ACCESS,
            ToolCapability.KNOWLEDGE_ACCESS,
        ),
    )

    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_output(route)


def test_non_string_reason_rejected():
    route = _route()
    object.__setattr__(route, "reason", 123)

    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_output(route)


def test_empty_reason_rejected():
    route = _route(reason="")

    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_output(route)


def test_whitespace_reason_rejected():
    route = _route(reason="   ")

    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_output(route)


def test_unsupported_tool_route_version_rejected():
    route = _route()
    object.__setattr__(route, "version", 2)

    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_output(route)


def test_knowledge_invariant_mismatch_rejected():
    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_routing_invariant(
            _plan(knowledge=True),
            _route(),
        )


def test_memory_invariant_mismatch_rejected():
    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_routing_invariant(
            _plan(memory=True),
            _route(),
        )


def test_session_invariant_mismatch_rejected():
    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_routing_invariant(
            _plan(session=True),
            _route(),
        )


def test_no_capability_invariant_mismatch_rejected():
    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_routing_invariant(
            _plan(),
            _route(
                capabilities=(ToolCapability.KNOWLEDGE_ACCESS,),
                reason="knowledge requirement routes to knowledge access capability",
            ),
        )


def test_exact_reason_mismatch_rejected():
    with pytest.raises(ToolRoutingValidationError):
        ToolRoutingValidator.validate_routing_invariant(
            _plan(knowledge=True),
            _route(
                capabilities=(ToolCapability.KNOWLEDGE_ACCESS,),
                reason="wrong reason",
            ),
        )
