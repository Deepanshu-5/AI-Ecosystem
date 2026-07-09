from dataclasses import FrozenInstanceError

import pytest

from routing.model_route import CURRENT_SCHEMA_VERSION, ModelRoute
from routing.model_target import ModelTarget


def test_model_route_construction():
    route = ModelRoute(
        target=ModelTarget.LIGHTWEIGHT,
        reason="low complexity routes to lightweight target",
    )

    assert route.target is ModelTarget.LIGHTWEIGHT
    assert route.reason == "low complexity routes to lightweight target"


def test_model_route_is_immutable():
    route = ModelRoute(
        target=ModelTarget.STANDARD,
        reason="medium complexity routes to standard target",
    )

    with pytest.raises(FrozenInstanceError):
        route.target = ModelTarget.ADVANCED


def test_model_route_default_schema_version():
    route = ModelRoute(
        target=ModelTarget.ADVANCED,
        reason="high complexity routes to advanced target",
    )

    assert route.version == CURRENT_SCHEMA_VERSION


def test_model_route_stable_serialization():
    route = ModelRoute(
        target=ModelTarget.ADVANCED,
        reason="high complexity routes to advanced target",
    )

    assert route.to_dict() == {
        "target": "advanced",
        "reason": "high complexity routes to advanced target",
        "version": CURRENT_SCHEMA_VERSION,
    }


def test_model_route_serialization_key_order():
    route = ModelRoute(
        target=ModelTarget.STANDARD,
        reason="medium complexity routes to standard target",
    )

    assert list(route.to_dict().keys()) == ["target", "reason", "version"]


def test_model_route_serializes_target_with_enum_value():
    route = ModelRoute(
        target=ModelTarget.LIGHTWEIGHT,
        reason="low complexity routes to lightweight target",
    )

    assert route.to_dict()["target"] == ModelTarget.LIGHTWEIGHT.value
