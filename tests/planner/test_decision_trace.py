from dataclasses import FrozenInstanceError

import pytest

from planner.decision_trace import DecisionTrace


def test_decision_trace_creation():
    trace = DecisionTrace(
        processing_goal_reason="Knowledge query.",
        complexity_reason="Simple lookup.",
        resource_requirements_reason="Knowledge retrieval required.",
    )

    assert trace.processing_goal_reason == "Knowledge query."
    assert trace.complexity_reason == "Simple lookup."
    assert (
        trace.resource_requirements_reason
        == "Knowledge retrieval required."
    )


def test_decision_trace_to_dict():
    trace = DecisionTrace(
        processing_goal_reason="Goal",
        complexity_reason="Complexity",
        resource_requirements_reason="Resources",
    )

    assert trace.to_dict() == {
        "processing_goal_reason": "Goal",
        "complexity_reason": "Complexity",
        "resource_requirements_reason": "Resources",
    }


def test_decision_trace_immutable():
    trace = DecisionTrace(
        processing_goal_reason="Goal",
        complexity_reason="Complexity",
        resource_requirements_reason="Resources",
    )

    with pytest.raises(FrozenInstanceError):
        trace.processing_goal_reason = "Modified"


def test_decision_trace_empty_strings():
    trace = DecisionTrace(
        processing_goal_reason="",
        complexity_reason="",
        resource_requirements_reason="",
    )

    assert trace.processing_goal_reason == ""
    assert trace.complexity_reason == ""
    assert trace.resource_requirements_reason == ""


def test_decision_trace_type():
    trace = DecisionTrace(
        processing_goal_reason="Goal",
        complexity_reason="Complexity",
        resource_requirements_reason="Resources",
    )

    assert isinstance(trace, DecisionTrace)