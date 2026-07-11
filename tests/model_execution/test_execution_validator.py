import pytest

from llm.base_generator import BaseGenerator
from model_execution.exceptions import ModelExecutionValidationError
from model_execution.execution_validator import ExecutionValidator
from model_execution.model_response import ModelResponse
from prompt_builder.prompt import Prompt
from routing.model_route import ModelRoute
from routing.model_target import ModelTarget


class _Generator(BaseGenerator):
    def generate(self, prompt: str) -> str:
        return "response"


def _route() -> ModelRoute:
    return ModelRoute(target=ModelTarget.LIGHTWEIGHT, reason="valid route")


def test_valid_execution_boundary_is_accepted() -> None:
    ExecutionValidator.validate_input(Prompt(content="prompt"), _route(), _Generator())
    ExecutionValidator.validate_output(ModelResponse(content="response"))


@pytest.mark.parametrize(
    "prompt, route, generator, expected",
    [
        ("not prompt", _route(), _Generator(), "expected Prompt"),
        (Prompt(content="", version=1), _route(), _Generator(), "must not be empty"),
        (Prompt(content="prompt", version=2), _route(), _Generator(), "unsupported Prompt"),
        (Prompt(content="prompt"), "not route", _Generator(), "expected ModelRoute"),
        (Prompt(content="prompt"), _route(), object(), "expected BaseGenerator"),
    ],
)
def test_invalid_execution_input_is_rejected(prompt, route, generator, expected) -> None:
    with pytest.raises(ModelExecutionValidationError, match=expected):
        ExecutionValidator.validate_input(prompt, route, generator)  # type: ignore[arg-type]


def test_invalid_execution_output_is_rejected() -> None:
    response = ModelResponse(content="response", version=2)

    with pytest.raises(ModelExecutionValidationError, match="unsupported ModelResponse"):
        ExecutionValidator.validate_output(response)
