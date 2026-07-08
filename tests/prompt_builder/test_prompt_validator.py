"""
tests/prompt_builder/test_prompt_validator.py

Unit tests for PromptValidator.
"""

from __future__ import annotations

import pytest

from budgeting.budget_metadata import BudgetMetadata
from budgeting.budgeted_context import BudgetedContext
from prompt_builder.exceptions import PromptValidationError
from prompt_builder.prompt import Prompt
from prompt_builder.prompt_validator import PromptValidator
from retriever.knowledge_context import KnowledgeContext
from retriever.memory_context import MemoryContext
from retriever.session_context import SessionContext


class TestPromptValidatorInput:
    def _make_meta(self, total_budget: int = 1000) -> BudgetMetadata:
        return BudgetMetadata(
            total_budget=total_budget,
            reserved_tokens=200,
            query_tokens=50,
            context_budget=750,
            used_context_tokens=0,
            remaining_tokens=750,
            knowledge_tokens=0,
            memory_tokens=0,
            session_tokens=0,
        )

    def _make_context(
        self,
        effective_query: str = "hello",
        version: int = 1,
    ) -> BudgetedContext:
        return BudgetedContext(
            knowledge=KnowledgeContext(items=(), metadata={}),
            memory=MemoryContext(entries=(), metadata={}),
            session=SessionContext(summary="", recent_messages=(), metadata={}),
            metadata=self._make_meta(),
            effective_query=effective_query,
            version=version,
        )

    def _validator(self) -> PromptValidator:
        return PromptValidator(token_counter=len)

    def test_valid_budgeted_context_passes(self) -> None:
        self._validator().validate_input(self._make_context())

    def test_non_budgeted_context_rejected(self) -> None:
        with pytest.raises(PromptValidationError) as exc_info:
            self._validator().validate_input("not context")  # type: ignore[arg-type]
        assert "expected BudgetedContext" in str(exc_info.value)

    def test_unsupported_budgeted_context_version_rejected(self) -> None:
        with pytest.raises(PromptValidationError) as exc_info:
            self._validator().validate_input(self._make_context(version=99))
        assert "unsupported BudgetedContext schema version" in str(exc_info.value)

    def test_non_string_effective_query_rejected(self) -> None:
        ctx = BudgetedContext(
            knowledge=KnowledgeContext(items=(), metadata={}),
            memory=MemoryContext(entries=(), metadata={}),
            session=SessionContext(summary="", recent_messages=(), metadata={}),
            metadata=self._make_meta(),
            effective_query=123,  # type: ignore[arg-type]
        )
        with pytest.raises(PromptValidationError) as exc_info:
            self._validator().validate_input(ctx)
        assert "effective_query: expected str" in str(exc_info.value)

    def test_empty_effective_query_rejected(self) -> None:
        with pytest.raises(PromptValidationError) as exc_info:
            self._validator().validate_input(self._make_context(effective_query=""))
        assert "effective_query: must not be empty" in str(exc_info.value)

    def test_whitespace_only_effective_query_rejected(self) -> None:
        with pytest.raises(PromptValidationError) as exc_info:
            self._validator().validate_input(self._make_context(effective_query="   "))
        assert "effective_query: must not be whitespace-only" in str(exc_info.value)


class TestPromptValidatorOutput:
    def _validator(self) -> PromptValidator:
        return PromptValidator(token_counter=len)

    def test_valid_prompt_accepted(self) -> None:
        prompt = Prompt(content="[QUERY]\nhello")
        self._validator().validate_output(prompt, total_budget=100)

    def test_non_prompt_rejected(self) -> None:
        with pytest.raises(PromptValidationError) as exc_info:
            self._validator().validate_output("not prompt", total_budget=100)  # type: ignore[arg-type]
        assert "expected Prompt" in str(exc_info.value)

    def test_empty_content_rejected(self) -> None:
        prompt = Prompt(content="")
        with pytest.raises(PromptValidationError) as exc_info:
            self._validator().validate_output(prompt, total_budget=100)
        assert "content: must not be empty" in str(exc_info.value)

    def test_whitespace_only_content_rejected(self) -> None:
        prompt = Prompt(content="   ")
        with pytest.raises(PromptValidationError) as exc_info:
            self._validator().validate_output(prompt, total_budget=100)
        assert "content: must not be whitespace-only" in str(exc_info.value)

    def test_unsupported_prompt_version_rejected(self) -> None:
        prompt = Prompt(content="[QUERY]\nhello", version=99)
        with pytest.raises(PromptValidationError) as exc_info:
            self._validator().validate_output(prompt, total_budget=100)
        assert "unsupported Prompt schema version" in str(exc_info.value)

    def test_exact_budget_prompt_accepted(self) -> None:
        content = "[QUERY]\nhello"
        prompt = Prompt(content=content)
        self._validator().validate_output(prompt, total_budget=len(content))

    def test_over_budget_prompt_rejected(self) -> None:
        content = "[QUERY]\nhello"
        prompt = Prompt(content=content)
        with pytest.raises(PromptValidationError) as exc_info:
            self._validator().validate_output(prompt, total_budget=len(content) - 1)
        assert "final prompt tokens" in str(exc_info.value)
        assert "exceed total_budget" in str(exc_info.value)

    def test_token_counter_is_deterministic(self) -> None:
        counter_calls: list[str] = []

        def counting(text: str) -> int:
            counter_calls.append(text)
            return len(text)

        validator = PromptValidator(token_counter=counting)
        prompt = Prompt(content="[QUERY]\nhello")
        validator.validate_output(prompt, total_budget=100)
        validator.validate_output(prompt, total_budget=100)
        assert counter_calls == ["[QUERY]\nhello", "[QUERY]\nhello"]

    def test_non_string_content_rejected(self) -> None:
        prompt = Prompt(content="[QUERY]\nhello")
        object.__setattr__(prompt, "content", 123)  # type: ignore[arg-type]
        with pytest.raises(PromptValidationError) as exc_info:
            self._validator().validate_output(prompt, total_budget=100)
        assert "content: expected str" in str(exc_info.value)
