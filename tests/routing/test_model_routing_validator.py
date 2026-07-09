import pytest

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.execution_plan import ExecutionPlan
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements
from routing.exceptions import ModelRoutingValidationError
from routing.model_route import ModelRoute
from routing.model_routing_validator import ModelRoutingValidator
from routing.model_target import ModelTarget


def _plan(
    complexity: Complexity = Complexity.LOW,
    processing_goal: ProcessingGoal = ProcessingGoal.GENERAL,
) -> ExecutionPlan:
    return ExecutionPlan(
        processing_goal=processing_goal,
        complexity=complexity,
        resource_requirements=ResourceRequirements(
            knowledge=False,
            memory=False,
            session=False,
        ),
        decision_trace=DecisionTrace(
            processing_goal_reason="General query.",
            complexity_reason="Simple lookup.",
            resource_requirements_reason="No retrieval is required.",
        ),
    )


def _route(target: ModelTarget = ModelTarget.LIGHTWEIGHT) -> ModelRoute:
    return ModelRoute(
        target=target,
        reason="low complexity routes to lightweight target",
    )


def test_valid_execution_plan_accepted():
    ModelRoutingValidator.validate_input(_plan())


def test_non_execution_plan_rejected():
    with pytest.raises(ModelRoutingValidationError):
        ModelRoutingValidator.validate_input("not a plan")


def test_unsupported_execution_plan_version_rejected():
    plan = _plan()
    object.__setattr__(plan, "version", 2)

    with pytest.raises(ModelRoutingValidationError):
        ModelRoutingValidator.validate_input(plan)


def test_invalid_execution_plan_complexity_rejected():
    plan = _plan()
    object.__setattr__(plan, "complexity", "low")

    with pytest.raises(ModelRoutingValidationError):
        ModelRoutingValidator.validate_input(plan)


def test_invalid_execution_plan_processing_goal_rejected():
    plan = _plan()
    object.__setattr__(plan, "processing_goal", "general")

    with pytest.raises(ModelRoutingValidationError):
        ModelRoutingValidator.validate_input(plan)


def test_valid_model_route_accepted():
    ModelRoutingValidator.validate_output(_route())


def test_non_model_route_rejected():
    with pytest.raises(ModelRoutingValidationError):
        ModelRoutingValidator.validate_output("not a route")


def test_invalid_model_target_rejected():
    route = _route()
    object.__setattr__(route, "target", "lightweight")

    with pytest.raises(ModelRoutingValidationError):
        ModelRoutingValidator.validate_output(route)


def test_non_string_reason_rejected():
    route = _route()
    object.__setattr__(route, "reason", 123)

    with pytest.raises(ModelRoutingValidationError):
        ModelRoutingValidator.validate_output(route)


def test_empty_reason_rejected():
    route = _route()
    object.__setattr__(route, "reason", "")

    with pytest.raises(ModelRoutingValidationError):
        ModelRoutingValidator.validate_output(route)


def test_whitespace_only_reason_rejected():
    route = _route()
    object.__setattr__(route, "reason", "   ")

    with pytest.raises(ModelRoutingValidationError):
        ModelRoutingValidator.validate_output(route)


def test_unsupported_model_route_version_rejected():
    route = _route()
    object.__setattr__(route, "version", 2)

    with pytest.raises(ModelRoutingValidationError):
        ModelRoutingValidator.validate_output(route)


def test_low_lightweight_invariant():
    ModelRoutingValidator.validate_routing_invariant(
        _plan(Complexity.LOW),
        _route(ModelTarget.LIGHTWEIGHT),
    )


def test_medium_standard_invariant():
    ModelRoutingValidator.validate_routing_invariant(
        _plan(Complexity.MEDIUM),
        ModelRoute(
            target=ModelTarget.STANDARD,
            reason="medium complexity routes to standard target",
        ),
    )


def test_high_advanced_invariant():
    ModelRoutingValidator.validate_routing_invariant(
        _plan(Complexity.HIGH),
        ModelRoute(
            target=ModelTarget.ADVANCED,
            reason="high complexity routes to advanced target",
        ),
    )


def test_complexity_target_mismatch_rejected():
    with pytest.raises(ModelRoutingValidationError):
        ModelRoutingValidator.validate_routing_invariant(
            _plan(Complexity.HIGH),
            _route(ModelTarget.LIGHTWEIGHT),
        )
