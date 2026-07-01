from dataclasses import FrozenInstanceError

import pytest

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.execution_plan import (
    CURRENT_SCHEMA_VERSION,
    ExecutionPlan,
)
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements


def create_execution_plan() -> ExecutionPlan:
    return ExecutionPlan(
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


def test_execution_plan_creation():
    plan = create_execution_plan()

    assert plan.processing_goal is ProcessingGoal.KNOWLEDGE
    assert plan.complexity is Complexity.LOW
    assert plan.resource_requirements.knowledge is True


def test_execution_plan_version():
    plan = create_execution_plan()

    assert plan.version == CURRENT_SCHEMA_VERSION


def test_execution_plan_to_dict():
    plan = create_execution_plan()

    assert plan.to_dict() == {
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
            "resource_requirements_reason":
                "Knowledge retrieval required.",
        },
        "version": CURRENT_SCHEMA_VERSION,
    }


def test_execution_plan_immutable():
    plan = create_execution_plan()

    with pytest.raises(FrozenInstanceError):
        plan.processing_goal = ProcessingGoal.CODE


def test_execution_plan_type():
    plan = create_execution_plan()

    assert isinstance(plan, ExecutionPlan)