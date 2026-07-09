"""
routing/exceptions.py

Domain exception hierarchy for the Model Routing subsystem.
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
