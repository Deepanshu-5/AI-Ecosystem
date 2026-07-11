"""
Deterministic runtime orchestration for Model Execution Integration.

Implementation justification:
    This new module is required by the frozen architecture. It performs only
    the specified forward transformation from Prompt and ModelRoute through
    BaseGenerator to ModelResponse, without assuming infrastructure ownership.
Runtime binding, provider selection, and runtime configuration remain outside
this subsystem and are owned by infrastructure.
"""

from __future__ import annotations

from llm.base_generator import BaseGenerator
from prompt_builder.prompt import Prompt
from routing.model_route import ModelRoute

from model_execution.exceptions import ModelExecutionError
from model_execution.execution_validator import ExecutionValidator
from model_execution.model_response import ModelResponse


class ModelExecutionIntegration:
    """
    Execute validated prompt content through a provider-neutral runtime.

    Purpose:
        Owns the deterministic execution boundary between Control Plane
        contracts and the runtime interface.

    Owned by:
        model_execution/model_execution_integration.py

    Consumed by:
        The downstream Control Plane execution caller.

    Invariants:
        - Consumes Prompt and ModelRoute without mutation or reinterpretation.
        - Invokes BaseGenerator exactly once for each successful validation.
        - Constructs exactly one immutable ModelResponse.
        - Does not instantiate, select, or configure runtimes.
    """

    def execute(
        self,
        prompt: Prompt,
        model_route: ModelRoute,
        generator: BaseGenerator,
    ) -> ModelResponse:
        """Execute a prompt using the supplied runtime implementation.

        Parameters:
            prompt: Immutable prompt created by Prompt Builder.
            model_route: Immutable semantic route created by Model Routing.
            generator: Provider-neutral runtime implementation to invoke.

        Returns:
            The validated immutable response from the runtime.

        Raises:
            ModelExecutionValidationError: If an execution boundary contract is
                invalid.
            ModelExecutionError: If runtime invocation fails.

        Side Effects:
            Invokes ``generator.generate`` once after validation succeeds.
        """
        # ModelRoute is validated at the execution boundary but is intentionally
        # not interpreted by this subsystem. Runtime binding is owned outside
        # Model Execution Integration by the infrastructure layer.
        ExecutionValidator.validate_input(prompt, model_route, generator)

        try:
            raw_response = generator.generate(prompt.content)
        except Exception as error:
            raise ModelExecutionError("Runtime invocation failed during model execution.") from error

        model_response = ModelResponse(content=raw_response)
        ExecutionValidator.validate_output(model_response)
        return model_response
