"""
retriever/exceptions.py

Domain exceptions raised by the Retrieval subsystem.
"""


class RetrieverError(Exception):
    """
    Base exception for all domain violations raised within the
    Retriever package.

    Purpose:
        Provides a single, importable root so callers can catch every
        Retriever-specific failure without depending on built-in
        exception types (ValueError, TypeError, RuntimeError), per
        Implementation Specification Section 8.

    Owned by:
        retriever/exceptions.py

    Consumed by:
        RetrievalValidator, RetrievalBuilder, individual retrievers,
        and any caller of the Retriever that needs to distinguish
        Retriever failures from unrelated exceptions.

    Invariants:
        - Carries a human-readable, deterministic message.
        - Never wraps or leaks infrastructure-level stack traces.
    """


class RetrievalValidationError(RetrieverError):
    """
    Raised when a candidate RetrievedContext fails structural,
    logical, or semantic validation.

    Purpose:
        Signals that RetrievalValidator rejected a candidate context.
        The caller (RetrievalBuilder) must not catch this to repair
        or infer a corrected value — per Implementation Specification
        Section 14, invalid input is reported, never silently
        corrected.

    Owned by:
        retriever/exceptions.py

    Consumed by:
        RetrievalBuilder.

    Invariants:
        - Always carries a message naming the specific field and rule
          that failed, for every violation found.
    """


class InvalidExecutionPlanError(RetrieverError):
    """
    Raised when the ExecutionPlan passed to the RetrievalBuilder is
    structurally invalid, missing required fields, or otherwise
    unsuitable for retrieval orchestration.

    Purpose:
        Signals that the upstream Planner produced an output that the
        Retriever cannot consume. This is a pipeline-level error, not
        a retrieval failure.

    Owned by:
        retriever/exceptions.py

    Consumed by:
        RetrievalBuilder.

    Invariants:
        - Always carries a message explaining which aspect of the
          ExecutionPlan is invalid.
    """


class UnsupportedSchemaVersionError(RetrieverError):
    """
    Raised when a RetrievedContext carries a schema version that the
    current RetrievalValidator does not recognize.

    Purpose:
        Signals that a RetrievedContext was produced by a different
        version of the retrieval subsystem and cannot be safely
        consumed.

    Owned by:
        retriever/exceptions.py

    Consumed by:
        RetrievalValidator.

    Invariants:
        - Always carries the unsupported version and the list of known
          versions.
    """
