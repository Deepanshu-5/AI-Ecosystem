"""
budgeting/exceptions.py

Domain exceptions raised by the Context Budgeting Layer.
"""


class ContextBudgetingError(Exception):
    """
    Base exception for all domain violations raised within the
    Budgeting package.

    Purpose:
        Provides a single, importable root so callers can catch every
        Budgeting-specific failure without depending on built-in
        exception types.

    Owned by:
        budgeting/exceptions.py
    """


class ContextBudgetValidationError(ContextBudgetingError):
    """
    Raised when input, configuration, or output state is invalid.

    Purpose:
        Signals that BudgetValidator rejected a candidate state.
        Invalid input is reported, never silently corrected.

    Owned by:
        budgeting/exceptions.py
    """


class ContextBudgetOverflowError(ContextBudgetingError):
    """
    Raised when a budget state cannot be satisfied under the explicit
    overflow policy.

    Purpose:
        Signals that the query budget is <= 0 after applying overflow
        policy, or another budget state is impossible to satisfy.

    Owned by:
        budgeting/exceptions.py
    """
