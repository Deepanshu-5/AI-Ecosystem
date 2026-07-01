"""
planner/exceptions.py

Domain exceptions raised by the Planner package.
"""


class PlannerError(Exception):
    """
    Base exception for all domain violations raised within the Planner
    package.

    Purpose:
        Provides a single, importable root so callers can catch every
        Planner-specific failure without depending on built-in exception
        types (ValueError, TypeError, RuntimeError), per Implementation
        Specification Section 8.

    Owned by:
        planner/exceptions.py

    Consumed by:
        PlannerValidator, PlannerBuilder, QueryAnalyzer (future), and any
        caller of the Planner that needs to distinguish Planner failures
        from unrelated exceptions.

    Invariants:
        - Carries a human-readable, deterministic message.
        - Never wraps or leaks infrastructure-level stack traces.
    """


class PlannerValidationError(PlannerError):
    """
    Raised when a candidate ExecutionPlan fails structural, logical, or
    semantic validation.

    Purpose:
        Signals that PlannerValidator rejected a candidate plan. The
        caller (PlannerBuilder) must not catch this to repair or infer
        a corrected value — per Implementation Specification Section 14,
        invalid input is reported, never silently corrected.

    Owned by:
        planner/exceptions.py

    Consumed by:
        PlannerBuilder.

    Invariants:
        - Always carries a message naming the specific field and rule
          that failed, for every violation found.
    """