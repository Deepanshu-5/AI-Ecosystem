"""
Pure execution-boundary validation for Model Execution Integration.

Implementation justification:
    This new internal module is required by the frozen architecture. It limits
    validation to execution-owned contract invariants and does not alter the
    ownership of Prompt, ModelRoute, or runtime infrastructure.
"""

from __future__ import annotations

from llm.base_generator import BaseGenerator
from prompt_builder.prompt import CURRENT_SCHEMA_VERSION as PROMPT_SCHEMA_VERSION
from prompt_builder.prompt import Prompt
from routing.model_route import CURRENT_SCHEMA_VERSION as MODEL_ROUTE_SCHEMA_VERSION
from routing.model_route import ModelRoute
from routing.model_target import ModelTarget

from model_execution.exceptions import ModelExecutionValidationError
from model_execution.model_response import (
    CURRENT_SCHEMA_VERSION as MODEL_RESPONSE_SCHEMA_VERSION,
)
from model_execution.model_response import ModelResponse

_KNOWN_PROMPT_VERSIONS = frozenset({PROMPT_SCHEMA_VERSION})
_KNOWN_MODEL_ROUTE_VERSIONS = frozenset({MODEL_ROUTE_SCHEMA_VERSION})
_KNOWN_MODEL_RESPONSE_VERSIONS = frozenset({MODEL_RESPONSE_SCHEMA_VERSION})


class ExecutionValidator:
    """
    Validate Model Execution Integration input and output contracts.

    Purpose:
        Enforces only execution-boundary assumptions without invoking runtime
        infrastructure or duplicating semantic validation owned upstream.

    Owned by:
        model_execution/execution_validator.py

    Consumed by:
        ModelExecutionIntegration.

    Invariants:
        - Pure and deterministic.
        - Never mutates inspected objects.
        - Never invokes a model or accesses configuration.
    """

    @staticmethod
    def validate_input(
        prompt: Prompt,
        model_route: ModelRoute,
        generator: BaseGenerator,
    ) -> None:
        """Validate the execution input boundary.

        Raises:
            ModelExecutionValidationError: If an execution contract invariant
                is violated.
        """
        violations: list[str] = []

        if not isinstance(prompt, Prompt):
            violations.append(f"prompt: expected Prompt, got {type(prompt).__name__}")
        else:
            if not isinstance(prompt.version, int):
                violations.append(
                    f"prompt.version: expected int, got {type(prompt.version).__name__}"
                )
            elif prompt.version not in _KNOWN_PROMPT_VERSIONS:
                violations.append(
                    f"prompt.version: unsupported Prompt schema version {prompt.version}"
                )

            if not isinstance(prompt.content, str):
                violations.append(
                    f"prompt.content: expected str, got {type(prompt.content).__name__}"
                )
            elif not prompt.content:
                violations.append("prompt.content: must not be empty")

        if not isinstance(model_route, ModelRoute):
            violations.append(
                f"model_route: expected ModelRoute, got {type(model_route).__name__}"
            )
        else:
            if not isinstance(model_route.version, int):
                violations.append(
                    "model_route.version: expected int, got "
                    f"{type(model_route.version).__name__}"
                )
            elif model_route.version not in _KNOWN_MODEL_ROUTE_VERSIONS:
                violations.append(
                    "model_route.version: unsupported ModelRoute schema version "
                    f"{model_route.version}"
                )

            if not isinstance(model_route.target, ModelTarget):
                violations.append(
                    "model_route.target: expected ModelTarget, got "
                    f"{type(model_route.target).__name__}"
                )

        if not isinstance(generator, BaseGenerator):
            violations.append(
                f"generator: expected BaseGenerator, got {type(generator).__name__}"
            )

        if violations:
            raise ModelExecutionValidationError(
                "Model Execution input validation failed:\n- " + "\n- ".join(violations)
            )

    @staticmethod
    def validate_output(model_response: ModelResponse) -> None:
        """Validate the canonical execution output contract.

        Raises:
            ModelExecutionValidationError: If an output contract invariant is
                violated.
        """
        violations: list[str] = []

        if not isinstance(model_response, ModelResponse):
            violations.append(
                "model_response: expected ModelResponse, got "
                f"{type(model_response).__name__}"
            )
        else:
            if not isinstance(model_response.version, int):
                violations.append(
                    "model_response.version: expected int, got "
                    f"{type(model_response.version).__name__}"
                )
            elif model_response.version not in _KNOWN_MODEL_RESPONSE_VERSIONS:
                violations.append(
                    "model_response.version: unsupported ModelResponse schema version "
                    f"{model_response.version}"
                )

            if model_response.content is None:
                violations.append("model_response.content: must not be None")
            elif not isinstance(model_response.content, str):
                violations.append(
                    "model_response.content: expected str, got "
                    f"{type(model_response.content).__name__}"
                )

        if violations:
            raise ModelExecutionValidationError(
                "Model Execution output validation failed:\n- " + "\n- ".join(violations)
            )
