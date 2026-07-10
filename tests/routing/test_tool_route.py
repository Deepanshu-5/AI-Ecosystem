from dataclasses import FrozenInstanceError

import pytest

from routing.tool_capability import ToolCapability
from routing.tool_route import CURRENT_SCHEMA_VERSION, ToolRoute


def test_tool_route_constructs_with_capabilities_and_reason():
    route = ToolRoute(
        capabilities=(
            ToolCapability.KNOWLEDGE_ACCESS,
            ToolCapability.MEMORY_ACCESS,
        ),
        reason="knowledge and memory requirements route to knowledge and memory access capabilities",
    )

    assert route.capabilities == (
        ToolCapability.KNOWLEDGE_ACCESS,
        ToolCapability.MEMORY_ACCESS,
    )
    assert route.reason == (
        "knowledge and memory requirements route to knowledge and memory "
        "access capabilities"
    )


def test_tool_route_is_immutable():
    route = ToolRoute(
        capabilities=(ToolCapability.KNOWLEDGE_ACCESS,),
        reason="knowledge requirement routes to knowledge access capability",
    )

    with pytest.raises(FrozenInstanceError):
        route.reason = "changed"


def test_tool_route_stores_capabilities_as_tuple():
    route = ToolRoute(
        capabilities=(ToolCapability.SESSION_ACCESS,),
        reason="session requirement routes to session access capability",
    )

    assert isinstance(route.capabilities, tuple)


def test_tool_route_accepts_empty_tuple():
    route = ToolRoute(
        capabilities=(),
        reason="no resource access capabilities required",
    )

    assert route.capabilities == ()


def test_tool_route_uses_default_version():
    route = ToolRoute(
        capabilities=(),
        reason="no resource access capabilities required",
    )

    assert route.version == CURRENT_SCHEMA_VERSION


def test_tool_route_serialization_is_stable():
    route = ToolRoute(
        capabilities=(
            ToolCapability.KNOWLEDGE_ACCESS,
            ToolCapability.MEMORY_ACCESS,
        ),
        reason="knowledge and memory requirements route to knowledge and memory access capabilities",
    )

    assert route.to_dict() == {
        "capabilities": [
            "knowledge_access",
            "memory_access",
        ],
        "reason": (
            "knowledge and memory requirements route to knowledge and memory "
            "access capabilities"
        ),
        "version": 1,
    }


def test_tool_route_serialization_key_order_is_exact():
    route = ToolRoute(
        capabilities=(),
        reason="no resource access capabilities required",
    )

    assert list(route.to_dict().keys()) == [
        "capabilities",
        "reason",
        "version",
    ]


def test_tool_route_serializes_capabilities_as_enum_values():
    route = ToolRoute(
        capabilities=(
            ToolCapability.KNOWLEDGE_ACCESS,
            ToolCapability.SESSION_ACCESS,
        ),
        reason="knowledge and session requirements route to knowledge and session access capabilities",
    )

    assert route.to_dict()["capabilities"] == [
        "knowledge_access",
        "session_access",
    ]
