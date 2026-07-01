from dataclasses import FrozenInstanceError

import pytest

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.planning_context import PlanningContext
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements


def create_context() -> PlanningContext:
    return PlanningContext(
        processing_goal=ProcessingGoal.KNOWLEDGE,
        complexity=Complexity.LOW,
        resource_requirements=ResourceRequirements(
            knowledge=True,
            memory=False,
            session=False,
        ),
        decision_trace=DecisionTrace(
            processing_goal_reason="Knowledge query.",
            complexity_reason="Simple lookup.",
            resource_requirements_reason="Knowledge retrieval required.",
        ),
    )


def test_planning_context_creation():
    context = create_context()

    assert context.processing_goal is ProcessingGoal.KNOWLEDGE
    assert context.complexity is Complexity.LOW
    assert context.resource_requirements.knowledge is True
    assert context.resource_requirements.memory is False
    assert context.resource_requirements.session is False


def test_planning_context_to_dict():
    context = create_context()

    assert context.to_dict() == {
        "processing_goal": "knowledge",
        "complexity": "low",
        "resource_requirements": {
            "knowledge": True,
            "memory": False,
            "session": False,
        },
        "decision_trace": {
            "processing_goal_reason": "Knowledge query.",
            "complexity_reason": "Simple lookup.",
            "resource_requirements_reason": "Knowledge retrieval required.",
        },
    }


def test_planning_context_immutable():
    context = create_context()

    with pytest.raises(FrozenInstanceError):
        context.processing_goal = ProcessingGoal.CODE


def test_planning_context_type():
    context = create_context()

    assert isinstance(context, PlanningContext)


def test_nested_objects():
    context = create_context()

    assert isinstance(
        context.resource_requirements,
        ResourceRequirements,
    )

    assert isinstance(
        context.decision_trace,
        DecisionTrace,
    )