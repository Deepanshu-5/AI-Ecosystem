from planner.complexity import Complexity


def test_complexity_members():
    expected = {
        "LOW",
        "MEDIUM",
        "HIGH",
    }

    assert {level.name for level in Complexity} == expected


def test_complexity_values():
    assert Complexity.LOW.value == "low"
    assert Complexity.MEDIUM.value == "medium"
    assert Complexity.HIGH.value == "high"


def test_complexity_member_count():
    assert len(Complexity) == 3


def test_complexity_type():
    for level in Complexity:
        assert isinstance(level, Complexity)


def test_complexity_unique_values():
    values = [level.value for level in Complexity]
    assert len(values) == len(set(values))