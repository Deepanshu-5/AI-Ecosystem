"""
budgeting/budget_validator.py

Validation for the Context Budgeting Layer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from budgeting.exceptions import ContextBudgetValidationError

if TYPE_CHECKING:
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
        Validate budgeting inputs and category-cap configuration.

        Raises:
            ContextBudgetValidationError:
                If one or more input invariants are violated.
        """
        from retriever.retrieved_context import RetrievedContext as _RetrievedContext

        violations: list[str] = []

        if not isinstance(retrieved_context, _RetrievedContext):
            violations.append(
                "retrieved_context: expected RetrievedContext, "
                f"got {type(retrieved_context).__name__}"
            )

        if not isinstance(query, str):
            violations.append(
                f"query: expected str, got {type(query).__name__}"
            )
        elif not query.strip():
            violations.append(
                "query: must not be empty or whitespace-only"
            )

        if (
            not isinstance(total_budget, int)
            or isinstance(total_budget, bool)
            or total_budget <= 0
        ):
            violations.append(
                "total_budget: must be a positive integer"
            )

        if (
            not isinstance(reserved_budget, int)
            or isinstance(reserved_budget, bool)
            or reserved_budget < 0
        ):
            violations.append(
                "reserved_budget: must be a non-negative integer"
            )

        if (
            isinstance(total_budget, int)
            and not isinstance(total_budget, bool)
            and isinstance(reserved_budget, int)
            and not isinstance(reserved_budget, bool)
            and reserved_budget >= total_budget
        ):
            violations.append(
                "reserved_budget: must be less than total_budget"
            )

        if category_caps is not None:
            expected_keys = {"knowledge", "memory", "session"}

            if not isinstance(category_caps, dict):
                violations.append(
                    "category_caps: expected dict"
                )
            else:
                actual_keys = set(category_caps.keys())

                if actual_keys != expected_keys:
                    violations.append(
                        "category_caps: must contain exactly "
                        "'knowledge', 'memory', and 'session'"
                    )
                else:
                    caps_are_numeric = True

                    for category, value in category_caps.items():
                        if (
                            not isinstance(value, (int, float))
                            or isinstance(value, bool)
                        ):
                            violations.append(
                                f"category_caps.{category}: must be numeric"
                            )
                            caps_are_numeric = False
                        elif value < 0:
                            violations.append(
                                f"category_caps.{category}: "
                                "must be non-negative"
                            )

                    if caps_are_numeric:
                        total = sum(category_caps.values())

                        if abs(total - 1.0) > 1e-9:
                            violations.append(
                                "category_caps: must total exactly 1.0"
                            )

        if violations:
            raise ContextBudgetValidationError(
                "Budget input validation failed:\n- "
                + "\n- ".join(violations)
            )

    @staticmethod
    def validate_output(
        budgeted_context: "BudgetedContext",
        context_budget: int,
        total_budget: int,
    ) -> None:
        """
        Validate BudgetedContext output invariants.

        Raises:
            ContextBudgetValidationError:
                If output structure or budgeting invariants are invalid.
        """
        from budgeting.budget_metadata import BudgetMetadata as _BudgetMetadata
        from budgeting.budgeted_context import BudgetedContext as _BudgetedContext
        from retriever.knowledge_context import KnowledgeContext
        from retriever.memory_context import MemoryContext
        from retriever.session_context import SessionContext

        if not isinstance(budgeted_context, _BudgetedContext):
            raise ContextBudgetValidationError(
                "Budget output validation failed:\n- "
                f"budgeted_context: expected BudgetedContext, got "
                f"{type(budgeted_context).__name__}"
            )

        violations: list[str] = []

        meta = budgeted_context.metadata

        if not isinstance(meta, _BudgetMetadata):
            raise ContextBudgetValidationError(
                "Budget output validation failed:\n- "
                f"metadata: expected BudgetMetadata, got "
                f"{type(meta).__name__}"
            )

        token_fields = (
            "total_budget",
            "reserved_tokens",
            "query_tokens",
            "context_budget",
            "used_context_tokens",
            "remaining_tokens",
            "knowledge_tokens",
            "memory_tokens",
            "session_tokens",
            "truncated_unit_count",
        )

        for field_name in token_fields:
            value = getattr(meta, field_name)

            if not isinstance(value, int) or isinstance(value, bool):
                violations.append(
                    f"metadata.{field_name}: expected non-negative int, "
                    f"got {type(value).__name__}"
                )
            elif value < 0:
                violations.append(
                    f"metadata.{field_name}: negative value {value} is invalid"
                )

        if not isinstance(meta.query_truncated, bool):
            violations.append(
                "metadata.query_truncated: expected bool"
            )

        if not isinstance(budgeted_context.knowledge, KnowledgeContext):
            violations.append(
                "knowledge: expected KnowledgeContext"
            )

        if not isinstance(budgeted_context.memory, MemoryContext):
            violations.append(
                "memory: expected MemoryContext"
            )

        if not isinstance(budgeted_context.session, SessionContext):
            violations.append(
                "session: expected SessionContext"
            )

        if not isinstance(budgeted_context.effective_query, str):
            violations.append(
                "effective_query: expected str"
            )
        elif not budgeted_context.effective_query.strip():
            violations.append(
                "effective_query: must not be empty or whitespace-only"
            )

        if violations:
            raise ContextBudgetValidationError(
                "Budget output validation failed:\n- "
                + "\n- ".join(violations)
            )

        if meta.total_budget != total_budget:
            violations.append(
                f"metadata.total_budget ({meta.total_budget}) does not equal "
                f"total_budget ({total_budget})"
            )

        if meta.context_budget != context_budget:
            violations.append(
                f"metadata.context_budget ({meta.context_budget}) does not equal "
                f"context_budget ({context_budget})"
            )

        if meta.used_context_tokens > context_budget:
            violations.append(
                f"used_context_tokens ({meta.used_context_tokens}) "
                f"exceeds context_budget ({context_budget})"
            )

        total_used = (
            meta.reserved_tokens
            + meta.query_tokens
            + meta.used_context_tokens
        )

        if total_used > total_budget:
            violations.append(
                f"total usage ({total_used}) exceeds total_budget "
                f"({total_budget})"
            )

        category_sum = (
            meta.knowledge_tokens
            + meta.memory_tokens
            + meta.session_tokens
        )

        if category_sum != meta.used_context_tokens:
            violations.append(
                f"category token sum ({category_sum}) does not equal "
                f"used_context_tokens ({meta.used_context_tokens})"
            )

        expected_remaining = context_budget - meta.used_context_tokens

        if meta.remaining_tokens != expected_remaining:
            violations.append(
                f"remaining_tokens ({meta.remaining_tokens}) does not equal "
                f"expected remaining budget ({expected_remaining})"
            )

        if violations:
            raise ContextBudgetValidationError(
                "Budget output validation failed:\n- "
                + "\n- ".join(violations)
            )