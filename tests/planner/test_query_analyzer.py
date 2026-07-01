import pytest

from planner.complexity import Complexity
from planner.exceptions import PlannerValidationError
from planner.processing_goal import ProcessingGoal
from planner.query_analyzer import QueryAnalyzer


def test_empty_query_raises():
    with pytest.raises(PlannerValidationError):
        QueryAnalyzer.analyze("   ")


def test_document_query():
    context = QueryAnalyzer.analyze(
        "Summarize the uploaded PDF document."
    )

    assert context.processing_goal is ProcessingGoal.DOCUMENT
    assert context.resource_requirements.knowledge is True


def test_memory_query():
    context = QueryAnalyzer.analyze(
        "What do you know about me?"
    )

    assert context.processing_goal is ProcessingGoal.MEMORY
    assert context.resource_requirements.memory is True


def test_session_query():
    context = QueryAnalyzer.analyze(
        "Continue our previous conversation."
    )

    assert context.processing_goal is ProcessingGoal.SESSION
    assert context.resource_requirements.session is True


def test_code_query():
    context = QueryAnalyzer.analyze(
        "Debug this Python function."
    )

    assert context.processing_goal is ProcessingGoal.CODE
    assert context.resource_requirements.knowledge is True


def test_knowledge_query():
    context = QueryAnalyzer.analyze(
        "What is machine learning?"
    )

    assert context.processing_goal is ProcessingGoal.KNOWLEDGE


def test_general_query():
    context = QueryAnalyzer.analyze(
        "Hello there."
    )

    assert context.processing_goal is ProcessingGoal.GENERAL


def test_high_complexity():
    context = QueryAnalyzer.analyze(
        "Design the architecture of a distributed system."
    )

    assert context.complexity is Complexity.HIGH


def test_medium_complexity():
    context = QueryAnalyzer.analyze(
        "Compare Python and Java."
    )

    assert context.complexity is Complexity.MEDIUM


def test_low_complexity():
    context = QueryAnalyzer.analyze(
        "What is Python?"
    )

    assert context.complexity is Complexity.LOW


def test_deterministic():
    query = "What is Python?"

    context1 = QueryAnalyzer.analyze(query)
    context2 = QueryAnalyzer.analyze(query)

    assert context1 == context2