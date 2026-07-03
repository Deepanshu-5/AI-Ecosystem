"""
budgeting/budget_validator.py

Validation for the Context Budgeting Layer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from budgeting.exceptions import ContextBudgetValidationError

if TYPE_CHECKING:
    from budgeting.budget_metadata import BudgetMetadata
    from budgeting.budgeted_context import BudgetedContext
    from retriever.retrieved_context import RetrievedContext


class BudgetValidator:
    """
    Validates Budgeting Layer inputs, configuration, and outputs.

    Purpose:
        Performs exhaustive validation of budget inputs, category
        caps, and BudgetedContext output. Reports every violation
        found in a single error. Never repairs or mutates state.

    Owned by:
        budgeting/budget_validator.py

    Invariants:
        - Performs no allocation.
        - Never mutates the objects it inspects.
        - Deterministic and side-effect-free.
    """

    @staticmethod
    def validate_input(
        retrieved_context: "RetrievedContext",
        query: str,
        total_budget: int,
        reserved_budget: int,
        category_caps: dict[str, float] | None,
    ) -> None:
        """
        Validate budgeting inputs.

        Parameters:
            retrieved_context: The RetrievedContext to budget.
            query: The original user query.
            total_budget: Maximum token budget.
            reserved_budget: Tokens reserved for Prompt Builder.
            category_caps: Optional custom category caps.

        Returns:
            None. Absence of exception means valid.

        Raises:
            ContextBudgetValidationError: If any input is invalid.
        """
        violations: list[str] = []

        from retriever.retrieved_context import RetrievedContext as _RC

        if not isinstance(retrieved_context, _RC):
            violations.append(
                f"retrieved_context: expected RetrievedContext, got "
                f"{type(retrieved_context).__name__}"
            )

        if not isinstance(query, str):
            violations.append(
                f"query: expected str, got {type(query).__name__}"
            )
        elif not query.strip():
            violations.append("query: must not be empty or whitespace-only")

        if not isinstance(total_budget, int) or total_budget <= 0:
            violations.append(
                f"total_budget: must be a positive integer, got {total_budget!r}"
            )

        if not isinstance(reserved_budget, int) or reserved_budget < 0:
            violations.append(
                f"reserved_budget: must be a non-negative integer, "
                f"got {reserved_budget!r}"
            )

        if reserved_budget >= total_budget:
            violations.append(
                f"reserved_budget ({reserved_budget}) must be less than "
                f"total_budget ({total_budget})"
            )

        if category_caps is not None:
            violations.extend(
                BudgetValidator._validate_category_caps(category_caps)
            )

        if violations:
            raise ContextBudgetValidationError(
                "Budget input validation failed:\n- "
                + "\n- ".join(violations)
            )

    @staticmethod
    def _validate_category_caps(caps: dict[str, float]) -> list[str]:
        """Validate category cap configuration."""
        violations: list[str] = []

        required_keys = {"knowledge", "memory", "session"}
        if set(caps.keys()) != required_keys:
            violations.append(
                f"category_caps: must contain exactly {required_keys}, "
                f"got {set(caps.keys())}"
            )

        total = 0.0
        for key in required_keys:
            value = caps.get(key)
            if value is None:
                continue
            if not isinstance(value, (int, float)):
                violations.append(
                    f"category_caps[{key!r}]: must be numeric, "
                    f"got {type(value).__name__}"
                )
                continue
            if value < 0:
                violations.append(
                    f"category_caps[{key!r}]: must be non-negative, "
                    f"got {value}"
                )
            total += float(value)

        if not violations and abs(total - 1.0) > 1e-9:
            violations.append(
                f"category_caps: must total exactly 1.0, got {total}"
            )

        return violations

    @staticmethod
    def validate_output(
        budgeted_context: "BudgetedContext",
        context_budget: int,
        total_budget: int,
    ) -> None:
        """
        Validate BudgetedContext output invariants.

        Parameters:
            budgeted_context: The output to validate.
            context_budget: The available context budget.
            total_budget: The total token budget.

        Returns:
            None. Absence of exception means valid.

        Raises:
            ContextBudgetValidationError: If output invariants are
                violated.
        """
        violations: list[str] = []
        meta = budgeted_context.metadata

        if meta.used_context_tokens > context_budget:
            violations.append(
                f"used_context_tokens ({meta.used_context_tokens}) "
                f"exceeds context_budget ({context_budget})"
            )

        total_used = meta.reserved_tokens + meta.query_tokens + meta.used_context_tokens
        if total_used > total_budget:
            violations.append(
                f"total usage ({total_used}) exceeds total_budget "
                f"({total_budget})"
            )

        if meta.remaining_tokens < 0:
            violations.append(
                f"remaining_tokens ({meta.remaining_tokens}) is negative"
            )

        if meta.knowledge_tokens < 0:
            violations.append(
                f"knowledge_tokens ({meta.knowledge_tokens}) is negative"
            )
        if meta.memory_tokens < 0:
            violations.append(
                f"memory_tokens ({meta.memory_tokens}) is negative"
            )
        if meta.session_tokens < 0:
            violations.append(
                f"session_tokens ({meta.session_tokens}) is negative"
            )

        category_sum = meta.knowledge_tokens + meta.memory_tokens + meta.session_tokens
        if category_sum != meta.used_context_tokens:
            violations.append(
                f"category token sum ({category_sum}) does not equal "
                f"used_context_tokens ({meta.used_context_tokens})"
            )

        if violations:
            raise ContextBudgetValidationError(
                "Budget output validation failed:\n- "
                + "\n- ".join(violations)
            )
