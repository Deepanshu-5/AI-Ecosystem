"""
prompt_builder/prompt_validator.py

Validation for the Prompt Builder boundary.
"""

from __future__ import annotations

from typing import Callable

from budgeting.budgeted_context import CURRENT_SCHEMA_VERSION as BUDGETED_CONTEXT_SCHEMA_VERSION
from budgeting.budgeted_context import BudgetedContext
from prompt_builder.exceptions import PromptValidationError
from prompt_builder.prompt import CURRENT_SCHEMA_VERSION as PROMPT_SCHEMA_VERSION
from prompt_builder.prompt import Prompt

_KNOWN_BUDGETED_CONTEXT_VERSIONS = frozenset({BUDGETED_CONTEXT_SCHEMA_VERSION})
_KNOWN_PROMPT_VERSIONS = frozenset({PROMPT_SCHEMA_VERSION})


class PromptValidator:
    """
    Validates Prompt Builder input assumptions and output invariants.

    Purpose:
        Performs boundary validation without duplicating BudgetValidator
        ownership. Never repairs or mutates state.
    """

    def __init__(self, token_counter: Callable[[str], int]) -> None:
        self._count_fn = token_counter

    def validate_input(self, budgeted_context: BudgetedContext) -> None:
        """
        Validate Prompt Builder input boundary.

        Raises:
            PromptValidationError: If input invariants are violated.
        """
        violations: list[str] = []

        if not isinstance(budgeted_context, BudgetedContext):
            violations.append(
                "budgeted_context: expected BudgetedContext, "
                f"got {type(budgeted_context).__name__}"
            )
            raise PromptValidationError(
                "Prompt Builder input validation failed:\n- "
                + "\n- ".join(violations)
            )

        if budgeted_context.version not in _KNOWN_BUDGETED_CONTEXT_VERSIONS:
            violations.append(
                f"version: unsupported BudgetedContext schema version "
                f"{budgeted_context.version}"
            )

        if not isinstance(budgeted_context.effective_query, str):
            violations.append(
                "effective_query: expected str, "
                f"got {type(budgeted_context.effective_query).__name__}"
            )
        elif not budgeted_context.effective_query:
            violations.append("effective_query: must not be empty")
        elif not budgeted_context.effective_query.strip():
            violations.append(
                "effective_query: must not be whitespace-only"
            )

        if violations:
            raise PromptValidationError(
                "Prompt Builder input validation failed:\n- "
                + "\n- ".join(violations)
            )

    def validate_output(self, prompt: Prompt, total_budget: int) -> None:
        """
        Validate Prompt output contract and final token limit.

        Raises:
            PromptValidationError: If output invariants are violated.
        """
        violations: list[str] = []

        if not isinstance(prompt, Prompt):
            violations.append(
                f"prompt: expected Prompt, got {type(prompt).__name__}"
            )
            raise PromptValidationError(
                "Prompt Builder output validation failed:\n- "
                + "\n- ".join(violations)
            )

        if not isinstance(prompt.content, str):
            violations.append(
                f"content: expected str, got {type(prompt.content).__name__}"
            )
        elif not prompt.content:
            violations.append("content: must not be empty")
        elif not prompt.content.strip():
            violations.append("content: must not be whitespace-only")

        if prompt.version not in _KNOWN_PROMPT_VERSIONS:
            violations.append(
                f"version: unsupported Prompt schema version {prompt.version}"
            )

        if violations:
            raise PromptValidationError(
                "Prompt Builder output validation failed:\n- "
                + "\n- ".join(violations)
            )

        final_tokens = self._count_fn(prompt.content)
        if final_tokens > total_budget:
            raise PromptValidationError(
                "Prompt Builder output validation failed:\n- "
                f"final prompt tokens ({final_tokens}) exceed "
                f"total_budget ({total_budget})"
            )
