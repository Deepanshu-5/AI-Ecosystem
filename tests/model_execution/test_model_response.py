from dataclasses import FrozenInstanceError

import pytest

from model_execution.model_response import CURRENT_SCHEMA_VERSION, ModelResponse


def test_model_response_is_immutable_and_versioned() -> None:
    response = ModelResponse(content="runtime output")

    assert response.version == CURRENT_SCHEMA_VERSION
    with pytest.raises(FrozenInstanceError):
        response.content = "changed"  # type: ignore[misc]


def test_model_response_serialization_is_stable() -> None:
    response = ModelResponse(content="runtime output")

    assert response.to_dict() == {"content": "runtime output", "version": 1}
    assert list(response.to_dict()) == ["content", "version"]
    assert response.to_dict() == response.to_dict()
