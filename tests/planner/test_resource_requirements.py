from dataclasses import FrozenInstanceError

import pytest

from planner.resource_requirements import ResourceRequirements


def test_resource_requirements_creation():
    resources = ResourceRequirements(
        knowledge=True,
        memory=False,
        session=True,
    )

    assert resources.knowledge is True
    assert resources.memory is False
    assert resources.session is True


def test_resource_requirements_to_dict():
    resources = ResourceRequirements(
        knowledge=True,
        memory=False,
        session=True,
    )

    assert resources.to_dict() == {
        "knowledge": True,
        "memory": False,
        "session": True,
    }


def test_resource_requirements_immutable():
    resources = ResourceRequirements(
        knowledge=True,
        memory=False,
        session=True,
    )

    with pytest.raises(FrozenInstanceError):
        resources.knowledge = False


def test_resource_requirements_all_false():
    resources = ResourceRequirements(
        knowledge=False,
        memory=False,
        session=False,
    )

    assert resources.to_dict() == {
        "knowledge": False,
        "memory": False,
        "session": False,
    }


def test_resource_requirements_all_true():
    resources = ResourceRequirements(
        knowledge=True,
        memory=True,
        session=True,
    )

    assert resources.to_dict() == {
        "knowledge": True,
        "memory": True,
        "session": True,
    }