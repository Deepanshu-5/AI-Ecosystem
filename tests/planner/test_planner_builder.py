import pytest

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.exceptions import PlannerValidationError
from planner.execution_plan import ExecutionPlan
from planner.planner_builder import PlannerBuilder
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements


def create_inputs():
    return (
        ProcessingGoal.KNOWLEDGE,
        Complexity.LOW,
        ResourceRequirements(
            knowledge=True,
            memory=False,
            session=False,
        ),
        DecisionTrace(
            processing_goal_reason="Knowledge query.",
            complexity_reason="Simple lookup.",
            resource_requirements_reason="Knowledge retrieval required.",
        ),
    )


def test_builder_returns_execution_plan():
    goal, complexity, resources, trace = create_inputs()

    plan = PlannerBuilder.build(
        processing_goal=goal,
        complexity=complexity,
        resource_requirements=resources,
        decision_trace=trace,
    )

    assert isinstance(plan, ExecutionPlan)


def test_builder_sets_all_fields():
    goal, complexity, resources, trace = create_inputs()

    plan = PlannerBuilder.build(
        processing_goal=goal,
        complexity=complexity,
        resource_requirements=resources,
        decision_trace=trace,
    )

    assert plan.processing_goal is goal
    assert plan.complexity is complexity
    assert plan.resource_requirements is resources
    assert plan.decision_trace is trace


def test_builder_validates_execution_plan():
    goal, complexity, resources, trace = create_inputs()

    plan = PlannerBuilder.build(
        processing_goal=goal,
        complexity=complexity,
        resource_requirements=resources,
        decision_trace=trace,
    )

    assert plan.version == 1


def test_builder_propagates_validation_error():
    goal, complexity, resources, _ = create_inputs()

    invalid_trace = DecisionTrace(
        processing_goal_reason="",
        complexity_reason="",
        resource_requirements_reason="",
    )

    with pytest.raises(PlannerValidationError):
        PlannerBuilder.build(
            processing_goal=goal,
            complexity=complexity,
            resource_requirements=resources,
            decision_trace=invalid_trace,
        )


def test_builder_is_deterministic():
    goal, complexity, resources, trace = create_inputs()

    plan1 = PlannerBuilder.build(
        processing_goal=goal,
        complexity=complexity,
        resource_requirements=resources,
        decision_trace=trace,
    )

    plan2 = PlannerBuilder.build(
        processing_goal=goal,
        complexity=complexity,
        resource_requirements=resources,
        decision_trace=trace,
    )

    assert plan1 == plan2