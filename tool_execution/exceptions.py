"""Domain exceptions owned by Tool Execution Integration."""


class ToolExecutionIntegrationError(Exception):
    """Base exception for provider-independent tool execution failures."""


class ToolExecutionValidationError(ToolExecutionIntegrationError):
    """Raised when the Tool Execution boundary is invalid."""


class ToolExecutionRuntimeError(ToolExecutionIntegrationError):
    """Raised when the runtime boundary cannot execute a capability."""


class UnsupportedToolRouteVersionError(ToolExecutionIntegrationError):
    """Raised when ToolRoute uses a schema version unsupported for execution."""
