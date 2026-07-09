import pytest

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.execution_plan import ExecutionPlan
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements
from routing.exceptions import ModelRoutingValidationError
from routing.model_route import ModelRoute
from routing.model_router import ModelRouter
from routing.model_target import ModelTarget


EXPECTED_ROUTES = {
    Complexity.LOW: (
        ModelTarget.LIGHTWEIGHT,
        "low complexity routes to lightweight target",
    ),
    Complexity.MEDIUM: (
        ModelTarget.STANDARD,
        "medium complexity routes to standard target",
    ),
    Complexity.HIGH: (
        ModelTarget.ADVANCED,
        "high complexity routes to advanced target",
    ),
}


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


@pytest.mark.parametrize("complexity", list(Complexity))
def test_model_router_exact_complexity_routing(complexity):
    route = ModelRouter.route(_plan(complexity=complexity))
    expected_target, _ = EXPECTED_ROUTES[complexity]

    assert route.target is expected_target


@pytest.mark.parametrize("complexity", list(Complexity))
def test_model_router_exact_reason_strings(complexity):
    route = ModelRouter.route(_plan(complexity=complexity))
    _, expected_reason = EXPECTED_ROUTES[complexity]

    assert route.reason == expected_reason


@pytest.mark.parametrize("processing_goal", list(ProcessingGoal))
@pytest.mark.parametrize("complexity", list(Complexity))
def test_all_processing_goals_preserve_complexity_only_mapping(
    processing_goal,
    complexity,
):
    route = ModelRouter.route(
        _plan(
            complexity=complexity,
            processing_goal=processing_goal,
        )
    )
    expected_target, expected_reason = EXPECTED_ROUTES[complexity]

    assert route.target is expected_target
    assert route.reason == expected_reason


def test_model_router_deterministic_replay():
    plan = _plan(complexity=Complexity.HIGH)

    assert ModelRouter.route(plan) == ModelRouter.route(plan)
    assert ModelRouter.route(plan).to_dict() == ModelRouter.route(plan).to_dict()


def test_model_router_does_not_mutate_execution_plan():
    plan = _plan(complexity=Complexity.MEDIUM)
    before = plan.to_dict()

    ModelRouter.route(plan)

    assert plan.to_dict() == before


def test_model_router_does_not_mutate_nested_planner_contracts():
    plan = _plan(complexity=Complexity.HIGH)
    resources_before = plan.resource_requirements.to_dict()
    trace_before = plan.decision_trace.to_dict()

    ModelRouter.route(plan)

    assert plan.resource_requirements.to_dict() == resources_before
    assert plan.decision_trace.to_dict() == trace_before


def test_model_router_returns_model_route():
    route = ModelRouter.route(_plan())

    assert isinstance(route, ModelRoute)


def test_model_router_rejects_invalid_input():
    with pytest.raises(ModelRoutingValidationError):
        ModelRouter.route("not a plan")


def test_model_router_has_no_default_route_behavior():
    plan = _plan()
    object.__setattr__(plan, "complexity", "unsupported")

    with pytest.raises(ModelRoutingValidationError):
        ModelRouter.route(plan)
