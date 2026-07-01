import pytest

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.exceptions import PlannerValidationError
from planner.execution_plan import ExecutionPlan
from planner.planner_validator import PlannerValidator
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements


def create_plan() -> ExecutionPlan:
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


def test_validator_accepts_valid_plan():
    plan = create_plan()

    PlannerValidator.validate(plan)


def test_validator_rejects_empty_processing_goal_reason():
    plan = create_plan()

    plan = ExecutionPlan(
        processing_goal=plan.processing_goal,
        complexity=plan.complexity,
        resource_requirements=plan.resource_requirements,
        decision_trace=DecisionTrace(
            processing_goal_reason="",
            complexity_reason="Simple lookup.",
            resource_requirements_reason="Knowledge retrieval required.",
        ),
    )

    with pytest.raises(PlannerValidationError):
        PlannerValidator.validate(plan)


def test_validator_rejects_empty_complexity_reason():
    plan = create_plan()

    plan = ExecutionPlan(
        processing_goal=plan.processing_goal,
        complexity=plan.complexity,
        resource_requirements=plan.resource_requirements,
        decision_trace=DecisionTrace(
            processing_goal_reason="Knowledge query.",
            complexity_reason="",
            resource_requirements_reason="Knowledge retrieval required.",
        ),
    )

    with pytest.raises(PlannerValidationError):
        PlannerValidator.validate(plan)


def test_validator_rejects_empty_resource_reason():
    plan = create_plan()

    plan = ExecutionPlan(
        processing_goal=plan.processing_goal,
        complexity=plan.complexity,
        resource_requirements=plan.resource_requirements,
        decision_trace=DecisionTrace(
            processing_goal_reason="Knowledge query.",
            complexity_reason="Simple lookup.",
            resource_requirements_reason="",
        ),
    )

    with pytest.raises(PlannerValidationError):
        PlannerValidator.validate(plan)


def test_validator_rejects_invalid_version():
    plan = ExecutionPlan(
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
        version=999,
    )

    with pytest.raises(PlannerValidationError):
        PlannerValidator.validate(plan)