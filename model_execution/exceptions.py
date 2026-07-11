"""
Provider-independent exceptions for Model Execution Integration.

Implementation justification:
    This new module is required by the frozen architecture so callers receive
    execution-domain failures without depending on runtime-provider exceptions.
"""


class ModelExecutionError(Exception):
    """
    Base exception for failures crossing the execution boundary.

    Purpose:
        Represents provider-independent Model Execution Integration failures.

    Owned by:
        model_execution/exceptions.py

    Consumed by:
        Model Execution Integration callers.

    Invariants:
        - Represents only execution-domain failures.
        - Does not expose provider-specific exception types as public contracts.
    """


class ModelExecutionValidationError(ModelExecutionError):
    """
    Raised when execution input or output contract validation fails.

    Purpose:
        Reports deterministic execution boundary violations.

    Owned by:
        model_execution/exceptions.py

    Consumed by:
        ExecutionValidator and Model Execution Integration callers.

    Invariants:
        - Inherits from ModelExecutionError.
        - Represents validation failure only.
    """
