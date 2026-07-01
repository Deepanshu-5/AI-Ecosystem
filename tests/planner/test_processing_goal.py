from planner.processing_goal import ProcessingGoal


def test_processing_goal_members():
    expected = {
        "GENERAL",
        "KNOWLEDGE",
        "MEMORY",
        "SESSION",
        "DOCUMENT",
        "CODE",
    }

    assert {goal.name for goal in ProcessingGoal} == expected


def test_processing_goal_values():
    assert ProcessingGoal.GENERAL.value == "general"
    assert ProcessingGoal.KNOWLEDGE.value == "knowledge"
    assert ProcessingGoal.MEMORY.value == "memory"
    assert ProcessingGoal.SESSION.value == "session"
    assert ProcessingGoal.DOCUMENT.value == "document"
    assert ProcessingGoal.CODE.value == "code"


def test_processing_goal_member_count():
    assert len(ProcessingGoal) == 6


def test_processing_goal_type():
    for goal in ProcessingGoal:
        assert isinstance(goal, ProcessingGoal)


def test_processing_goal_unique_values():
    values = [goal.value for goal in ProcessingGoal]
    assert len(values) == len(set(values))