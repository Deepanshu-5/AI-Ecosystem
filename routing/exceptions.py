"""
routing/exceptions.py

Domain exception hierarchies for Routing subsystems.
"""


class ModelRoutingError(Exception):
    """
    Base exception for Model Routing failures.

    Purpose:
        Provides the single public root for Model Routing domain errors.

    Owned by:
        routing/exceptions.py

    Consumed by:
        Model Routing callers and tests.

    Invariants:
        - Represents only Model Routing failures.
        - Does not represent provider, model execution, timeout, retry,
          fallback, or infrastructure failures.
    """


class ModelRoutingValidationError(ModelRoutingError):
    """
    Raised when Model Routing validation rejects input or output state.

    Purpose:
        Reports boundary, output, and routing invariant violations.

    Owned by:
        routing/exceptions.py

    Consumed by:
        ModelRoutingValidator, ModelRouter callers, and tests.

    Invariants:
        - Inherits from ModelRoutingError.
        - Represents explicit validation failure only.
    """


class ToolRoutingError(Exception):
    """
    Base exception for Tool Routing failures.

    Purpose:
        Provides the single public root for Tool Routing domain errors.

    Owned by:
        routing/exceptions.py

    Consumed by:
        Tool Routing callers and tests.

    Invariants:
        - Represents only Tool Routing failures.
        - Does not represent tool discovery, runtime resolution, tool
          execution, timeout, retry, fallback, or infrastructure failures.
    """


class ToolRoutingValidationError(ToolRoutingError):
    """
    Raised when Tool Routing validation rejects input or output state.

    Purpose:
        Reports boundary, output, and routing invariant violations.

    Owned by:
        routing/exceptions.py

    Consumed by:
        ToolRoutingValidator, ToolRouter callers, and tests.

    Invariants:
        - Inherits from ToolRoutingError.
        - Represents explicit validation failure only.
    """
