from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Import frozen public contracts for typing clarity (treated as opaque by this component)
from model_execution.model_response import ModelResponse
from tool_execution.tool_execution_result import ToolExecutionResult

CURRENT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ControlPlaneResult:
    """Immutable public contract representing one completed Control Plane
    execution.

    This is a pure data contract (no orchestration, composition, or lifecycle
    logic here). It is versioned and contains optional branch results per the
    architecture.
    """

    model_response: ModelResponse | None
    tool_execution_result: ToolExecutionResult | None
    version: int = CURRENT_SCHEMA_VERSION


class ResultComposer:
    """Internal Result Composer component.

    Responsibility:
        Compose an immutable ControlPlaneResult from completed subsystem output
        contracts. This component performs no semantic interpretation and
        does not mutate the supplied subsystem outputs.
    """

    def compose(
        self,
        model_response: ModelResponse | None,
        tool_execution_result: ToolExecutionResult | None,
    ) -> ControlPlaneResult:
        return ControlPlaneResult(model_response=model_response, tool_execution_result=tool_execution_result)
