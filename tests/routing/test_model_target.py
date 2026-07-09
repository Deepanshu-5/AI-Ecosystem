from routing.model_target import ModelTarget


def test_model_target_exact_membership():
    assert list(ModelTarget) == [
        ModelTarget.LIGHTWEIGHT,
        ModelTarget.STANDARD,
        ModelTarget.ADVANCED,
    ]


def test_model_target_exact_values():
    assert ModelTarget.LIGHTWEIGHT.value == "lightweight"
    assert ModelTarget.STANDARD.value == "standard"
    assert ModelTarget.ADVANCED.value == "advanced"


def test_model_target_values_are_unique():
    values = [
        target.value
        for target in ModelTarget.__members__.values()
    ]

    assert len(values) == len(set(values))
