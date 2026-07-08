"""
prompt_builder/prompt_builder.py

Deterministic transformation from BudgetedContext to Prompt.
"""

from __future__ import annotations

from typing import Callable

from budgeting.budgeted_context import BudgetedContext
from prompt_builder.prompt import CURRENT_SCHEMA_VERSION, Prompt
from prompt_builder.prompt_validator import PromptValidator


class PromptBuilder:
    """
    Transforms BudgetedContext into a deterministic, model-ready Prompt.

    Purpose:
        Owns prompt assembly, section ordering, empty-section omission,
        effective-query placement, and final prompt validation.

    Invariants:
        - Never retrieves, budgets, routes, or executes models.
        - Never mutates BudgetedContext or nested domain objects.
        - Deterministic for identical inputs.
    """

    def __init__(
        self,
        token_counter: Callable[[str], int] | None = None,
    ) -> None:
        if token_counter is None:
            from shared.token_counter import token_counter as _tc

            count_fn = _tc.count
        else:
            count_fn = token_counter

        self._validator = PromptValidator(token_counter=count_fn)

    def build(self, budgeted_context: BudgetedContext) -> Prompt:
        """
        Assemble and validate a Prompt from BudgetedContext.

        Parameters:
            budgeted_context: The immutable budgeted context to transform.

        Returns:
            Prompt: Validated, immutable prompt.

        Raises:
            PromptValidationError: If input or output validation fails.
        """
        self._validator.validate_input(budgeted_context)

        sections: list[str] = []

        knowledge_section = _assemble_knowledge(budgeted_context.knowledge)
        if knowledge_section is not None:
            sections.append(knowledge_section)

        memory_section = _assemble_memory(budgeted_context.memory)
        if memory_section is not None:
            sections.append(memory_section)

        session_section = _assemble_session(budgeted_context.session)
        if session_section is not None:
            sections.append(session_section)

        sections.append(_assemble_query(budgeted_context.effective_query))

        content = "\n\n".join(sections)
        prompt = Prompt(content=content, version=CURRENT_SCHEMA_VERSION)

        self._validator.validate_output(
            prompt,
            budgeted_context.metadata.total_budget,
        )

        return prompt


def _assemble_knowledge(knowledge) -> str | None:
    if not knowledge.items:
        return None

    body = "\n".join(item.text for item in knowledge.items)
    return f"[KNOWLEDGE]\n{body}"


def _assemble_memory(memory) -> str | None:
    if not memory.entries:
        return None

    body = "\n".join(entry.content for entry in memory.entries)
    return f"[MEMORY]\n{body}"


def _assemble_session(session) -> str | None:
    if not session.summary and not session.recent_messages:
        return None

    parts: list[str] = []
    if session.summary:
        parts.append(f"Summary: {session.summary}")

    for message in session.recent_messages:
        parts.append(f"{message.role}: {message.content}")

    body = "\n".join(parts)
    return f"[SESSION]\n{body}"


def _assemble_query(effective_query: str) -> str:
    return f"[QUERY]\n{effective_query}"
