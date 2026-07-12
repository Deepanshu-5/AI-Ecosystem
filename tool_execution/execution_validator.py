"""Pure validation for Tool Execution Integration boundaries."""

from __future__ import annotations

from collections.abc import Mapping

from routing.tool_capability import ToolCapability
from routing.tool_route import CURRENT_SCHEMA_VERSION as TOOL_ROUTE_SCHEMA_VERSION
from routing.tool_route import ToolRoute
from tool_execution.exceptions import (
    ToolExecutionValidationError,
    UnsupportedToolRouteVersionError,
)
from tool_execution.runtime_executor import RuntimeExecutor
from tool_execution.tool_execution_result import (
    CURRENT_SCHEMA_VERSION as TOOL_EXECUTION_RESULT_SCHEMA_VERSION,
)
from tool_execution.tool_execution_result import ToolExecutionResult
from tool_execution.tool_result import CURRENT_SCHEMA_VERSION as TOOL_RESULT_SCHEMA_VERSION
from tool_execution.tool_result import ToolResult

_KNOWN_TOOL_ROUTE_VERSIONS = frozenset({TOOL_ROUTE_SCHEMA_VERSION})
_KNOWN_TOOL_RESULT_VERSIONS = frozenset({TOOL_RESULT_SCHEMA_VERSION})
_KNOWN_EXECUTION_RESULT_VERSIONS = frozenset({TOOL_EXECUTION_RESULT_SCHEMA_VERSION})
_CANONICAL_CAPABILITY_ORDER = (
    ToolCapability.KNOWLEDGE_ACCESS,
    ToolCapability.MEMORY_ACCESS,
    ToolCapability.SESSION_ACCESS,
)


class ExecutionValidator:
    """Validate only immutable Tool Execution Integration contracts."""

    @staticmethod
    def validate_input(tool_route: ToolRoute, runtime_executor: RuntimeExecutor) -> None:
        """Validate the accepted ToolRoute and available runtime boundary."""
        violations: list[str] = []

        if not isinstance(tool_route, ToolRoute):
            violations.append(
                f"tool_route: expected ToolRoute, got {type(tool_route).__name__}"
            )
        else:
            ExecutionValidator._validate_tool_route(violations, tool_route)

        if not isinstance(runtime_executor, RuntimeExecutor):
            violations.append(
                "runtime_executor: expected RuntimeExecutor, got "
                f"{type(runtime_executor).__name__}"
            )

        if violations:
            if isinstance(tool_route, ToolRoute) and any(
                violation.startswith("tool_route.version: unsupported")
                for violation in violations
            ):
                raise UnsupportedToolRouteVersionError(
                    "ToolRoute version validation failed:\n- "
                    + "\n- ".join(violations)
                )
            raise ToolExecutionValidationError(
                "Tool Execution input validation failed:\n- "
                + "\n- ".join(violations)
            )

    @staticmethod
    def validate_output(
        tool_execution_result: ToolExecutionResult,
        tool_route: ToolRoute,
    ) -> None:
        """Validate a completed execution result against its ToolRoute."""
        violations: list[str] = []

        if not isinstance(tool_execution_result, ToolExecutionResult):
            violations.append(
                "tool_execution_result: expected ToolExecutionResult, got "
                f"{type(tool_execution_result).__name__}"
            )
        else:
            ExecutionValidator._validate_execution_result(
                violations, tool_execution_result
            )

        if isinstance(tool_route, ToolRoute) and isinstance(
            tool_execution_result, ToolExecutionResult
        ):
            expected = tool_route.capabilities
            actual = tuple(result.capability for result in tool_execution_result.results)
            if actual != expected:
                violations.append(
                    "results: capabilities must match ToolRoute ordering exactly"
                )

        if violations:
            raise ToolExecutionValidationError(
                "Tool Execution output validation failed:\n- "
                + "\n- ".join(violations)
            )

    @staticmethod
    def _validate_tool_route(violations: list[str], tool_route: ToolRoute) -> None:
        if not isinstance(tool_route.version, int):
            violations.append(
                "tool_route.version: expected int, got "
                f"{type(tool_route.version).__name__}"
            )
        elif tool_route.version not in _KNOWN_TOOL_ROUTE_VERSIONS:
            violations.append(
                "tool_route.version: unsupported ToolRoute schema version "
                f"{tool_route.version}"
            )

        capabilities = tool_route.capabilities
        if not isinstance(capabilities, tuple):
            violations.append(
                "tool_route.capabilities: expected tuple, got "
                f"{type(capabilities).__name__}"
            )
            return

        if not all(isinstance(capability, ToolCapability) for capability in capabilities):
            violations.append("tool_route.capabilities: expected ToolCapability members")
            return
        if len(set(capabilities)) != len(capabilities):
            violations.append("tool_route.capabilities: duplicate capability is not allowed")
        canonical_positions = {
            capability: index
            for index, capability in enumerate(_CANONICAL_CAPABILITY_ORDER)
        }
        if tuple(sorted(capabilities, key=canonical_positions.__getitem__)) != capabilities:
            violations.append("tool_route.capabilities: must be in canonical order")

    @staticmethod
    def _validate_execution_result(
        violations: list[str], tool_execution_result: ToolExecutionResult
    ) -> None:
        if not isinstance(tool_execution_result.version, int):
            violations.append(
                "tool_execution_result.version: expected int, got "
                f"{type(tool_execution_result.version).__name__}"
            )
        elif tool_execution_result.version not in _KNOWN_EXECUTION_RESULT_VERSIONS:
            violations.append(
                "tool_execution_result.version: unsupported ToolExecutionResult "
                f"schema version {tool_execution_result.version}"
            )

        if not isinstance(tool_execution_result.results, tuple):
            violations.append(
                "tool_execution_result.results: expected tuple, got "
                f"{type(tool_execution_result.results).__name__}"
            )
            return
        for index, result in enumerate(tool_execution_result.results):
            ExecutionValidator._validate_tool_result(violations, index, result)

    @staticmethod
    def _validate_tool_result(
        violations: list[str], index: int, result: object
    ) -> None:
        prefix = f"tool_execution_result.results[{index}]"
        if not isinstance(result, ToolResult):
            violations.append(f"{prefix}: expected ToolResult, got {type(result).__name__}")
            return
        if not isinstance(result.capability, ToolCapability):
            violations.append(f"{prefix}.capability: expected ToolCapability")
        if not isinstance(result.version, int):
            violations.append(f"{prefix}.version: expected int")
        elif result.version not in _KNOWN_TOOL_RESULT_VERSIONS:
            violations.append(f"{prefix}.version: unsupported ToolResult schema version")
        if not isinstance(result.payload, Mapping):
            violations.append(f"{prefix}.payload: expected Mapping")
        elif not ExecutionValidator._is_serializable(result.payload):
            violations.append(f"{prefix}.payload: must contain only Serializable values")

    @staticmethod
    def _is_serializable(value: object) -> bool:
        if value is None or type(value) in (str, int, float, bool):
            return True
        if isinstance(value, list):
            return all(ExecutionValidator._is_serializable(item) for item in value)
        if isinstance(value, dict):
            return all(
                isinstance(key, str) and ExecutionValidator._is_serializable(item)
                for key, item in value.items()
            )
        return False
