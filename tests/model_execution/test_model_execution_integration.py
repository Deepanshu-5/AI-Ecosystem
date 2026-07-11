import pytest

from llm.base_generator import BaseGenerator
from model_execution.exceptions import ModelExecutionError, ModelExecutionValidationError
from model_execution.model_execution_integration import ModelExecutionIntegration
from prompt_builder.prompt import Prompt
from routing.model_route import ModelRoute
from routing.model_target import ModelTarget


class _RecordingGenerator(BaseGenerator):
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return "runtime output"


class _FailingGenerator(BaseGenerator):
    def generate(self, prompt: str) -> str:
        raise RuntimeError("provider failure")


def _route() -> ModelRoute:
    return ModelRoute(target=ModelTarget.STANDARD, reason="valid route")


def test_execution_forwards_prompt_once_without_mutating_contracts() -> None:
    prompt = Prompt(content="[QUERY]\nhello")
    route = _route()
    generator = _RecordingGenerator()

    response = ModelExecutionIntegration().execute(prompt, route, generator)

    assert generator.prompts == [prompt.content]
    assert response.content == "runtime output"
    assert prompt.content == "[QUERY]\nhello"
    assert route == _route()


def test_runtime_exception_is_translated_to_execution_error() -> None:
    with pytest.raises(ModelExecutionError, match="Runtime invocation failed during model execution.") as error:
        ModelExecutionIntegration().execute(Prompt(content="prompt"), _route(), _FailingGenerator())

    assert isinstance(error.value.__cause__, RuntimeError)


def test_validation_failure_stops_runtime_invocation() -> None:
    generator = _RecordingGenerator()

    with pytest.raises(ModelExecutionValidationError):
        ModelExecutionIntegration().execute(Prompt(content=""), _route(), generator)

    assert generator.prompts == []
