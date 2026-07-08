"""
tests/prompt_builder/test_prompt_builder.py

Unit tests for PromptBuilder assembly and validation.
"""

from __future__ import annotations

import copy

import pytest

from budgeting.budget_metadata import BudgetMetadata
from budgeting.budgeted_context import BudgetedContext
from prompt_builder.exceptions import PromptValidationError
from prompt_builder.prompt import Prompt
from prompt_builder.prompt_builder import PromptBuilder
from retriever.knowledge_context import KnowledgeContext, KnowledgeItem
from retriever.memory_context import MemoryContext, MemoryEntry
from retriever.session_context import SessionContext, SessionMessage


class TestPromptBuilder:
    def _make_meta(self, total_budget: int = 10000) -> BudgetMetadata:
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
        *,
        knowledge_items: tuple[KnowledgeItem, ...] = (),
        memory_entries: tuple[MemoryEntry, ...] = (),
        session_summary: str = "",
        session_messages: tuple[SessionMessage, ...] = (),
        effective_query: str = "What is Python?",
        total_budget: int = 10000,
    ) -> BudgetedContext:
        return BudgetedContext(
            knowledge=KnowledgeContext(items=knowledge_items, metadata={}),
            memory=MemoryContext(entries=memory_entries, metadata={}),
            session=SessionContext(
                summary=session_summary,
                recent_messages=session_messages,
                metadata={},
            ),
            metadata=self._make_meta(total_budget=total_budget),
            effective_query=effective_query,
        )

    def _builder(self) -> PromptBuilder:
        return PromptBuilder(token_counter=len)

    def test_query_only_prompt(self) -> None:
        ctx = self._make_context()
        prompt = self._builder().build(ctx)
        assert prompt.content == "[QUERY]\nWhat is Python?"

    def test_knowledge_only_context_plus_query(self) -> None:
        ctx = self._make_context(
            knowledge_items=(
                KnowledgeItem(text="Python is a language.", source="doc1", score=0.9),
            ),
        )
        prompt = self._builder().build(ctx)
        assert prompt.content == (
            "[KNOWLEDGE]\nPython is a language.\n\n[QUERY]\nWhat is Python?"
        )

    def test_memory_only_context_plus_query(self) -> None:
        ctx = self._make_context(
            memory_entries=(MemoryEntry(content="User prefers concise answers."),),
        )
        prompt = self._builder().build(ctx)
        assert prompt.content == (
            "[MEMORY]\nUser prefers concise answers.\n\n[QUERY]\nWhat is Python?"
        )

    def test_session_summary_only_context_plus_query(self) -> None:
        ctx = self._make_context(session_summary="User is learning Python.")
        prompt = self._builder().build(ctx)
        assert prompt.content == (
            "[SESSION]\nSummary: User is learning Python.\n\n[QUERY]\nWhat is Python?"
        )

    def test_session_messages_only_context_plus_query(self) -> None:
        ctx = self._make_context(
            session_messages=(
                SessionMessage(role="user", content="Explain Python."),
            ),
        )
        prompt = self._builder().build(ctx)
        assert prompt.content == (
            "[SESSION]\nuser: Explain Python.\n\n[QUERY]\nWhat is Python?"
        )

    def test_full_context_prompt(self) -> None:
        ctx = self._make_context(
            knowledge_items=(KnowledgeItem(text="FactA", source="doc1"),),
            memory_entries=(MemoryEntry(content="PrefA"),),
            session_summary="Summary text",
            session_messages=(
                SessionMessage(role="user", content="Hello"),
                SessionMessage(role="assistant", content="Hi there"),
            ),
        )
        prompt = self._builder().build(ctx)
        assert prompt.content == (
            "[KNOWLEDGE]\nFactA\n\n"
            "[MEMORY]\nPrefA\n\n"
            "[SESSION]\nSummary: Summary text\n"
            "user: Hello\n"
            "assistant: Hi there\n\n"
            "[QUERY]\nWhat is Python?"
        )

    def test_fixed_section_order(self) -> None:
        ctx = self._make_context(
            knowledge_items=(KnowledgeItem(text="K", source="d"),),
            memory_entries=(MemoryEntry(content="M"),),
            session_summary="S",
        )
        prompt = self._builder().build(ctx)
        knowledge_idx = prompt.content.index("[KNOWLEDGE]")
        memory_idx = prompt.content.index("[MEMORY]")
        session_idx = prompt.content.index("[SESSION]")
        query_idx = prompt.content.index("[QUERY]")
        assert knowledge_idx < memory_idx < session_idx < query_idx

    def test_empty_knowledge_section_omitted(self) -> None:
        ctx = self._make_context(
            memory_entries=(MemoryEntry(content="M"),),
        )
        prompt = self._builder().build(ctx)
        assert "[KNOWLEDGE]" not in prompt.content

    def test_empty_memory_section_omitted(self) -> None:
        ctx = self._make_context(
            knowledge_items=(KnowledgeItem(text="K", source="d"),),
        )
        prompt = self._builder().build(ctx)
        assert "[MEMORY]" not in prompt.content

    def test_empty_session_section_omitted(self) -> None:
        ctx = self._make_context(
            knowledge_items=(KnowledgeItem(text="K", source="d"),),
        )
        prompt = self._builder().build(ctx)
        assert "[SESSION]" not in prompt.content

    def test_query_always_emitted(self) -> None:
        ctx = self._make_context()
        prompt = self._builder().build(ctx)
        assert "[QUERY]" in prompt.content

    def test_query_always_last(self) -> None:
        ctx = self._make_context(
            knowledge_items=(KnowledgeItem(text="K", source="d"),),
            memory_entries=(MemoryEntry(content="M"),),
            session_summary="S",
        )
        prompt = self._builder().build(ctx)
        assert prompt.content.endswith("What is Python?")
        assert prompt.content.rindex("[QUERY]") > prompt.content.index("[SESSION]")

    def test_effective_query_used_exactly(self) -> None:
        ctx = self._make_context(effective_query="  trimmed upstream?  ")
        prompt = self._builder().build(ctx)
        assert prompt.content == "[QUERY]\n  trimmed upstream?  "

    def test_knowledge_item_order_preserved(self) -> None:
        ctx = self._make_context(
            knowledge_items=(
                KnowledgeItem(text="First", source="a"),
                KnowledgeItem(text="Second", source="b"),
                KnowledgeItem(text="Third", source="c"),
            ),
        )
        prompt = self._builder().build(ctx)
        assert "[KNOWLEDGE]\nFirst\nSecond\nThird" in prompt.content

    def test_knowledge_text_preserved_exactly(self) -> None:
        text = "  Leading spaces\tand punctuation!  "
        ctx = self._make_context(
            knowledge_items=(KnowledgeItem(text=text, source="doc"),),
        )
        prompt = self._builder().build(ctx)
        assert f"[KNOWLEDGE]\n{text}" in prompt.content

    def test_knowledge_source_not_emitted(self) -> None:
        ctx = self._make_context(
            knowledge_items=(KnowledgeItem(text="Fact", source="secret-doc"),),
        )
        prompt = self._builder().build(ctx)
        assert "secret-doc" not in prompt.content

    def test_knowledge_score_not_emitted(self) -> None:
        ctx = self._make_context(
            knowledge_items=(KnowledgeItem(text="Fact", source="doc", score=0.99),),
        )
        prompt = self._builder().build(ctx)
        assert "0.99" not in prompt.content

    def test_memory_entry_order_preserved(self) -> None:
        ctx = self._make_context(
            memory_entries=(
                MemoryEntry(content="Alpha"),
                MemoryEntry(content="Beta"),
            ),
        )
        prompt = self._builder().build(ctx)
        assert "[MEMORY]\nAlpha\nBeta" in prompt.content

    def test_memory_content_preserved_exactly(self) -> None:
        content = "  memory with spaces  "
        ctx = self._make_context(
            memory_entries=(MemoryEntry(content=content),),
        )
        prompt = self._builder().build(ctx)
        assert f"[MEMORY]\n{content}" in prompt.content

    def test_session_summary_precedes_messages(self) -> None:
        ctx = self._make_context(
            session_summary="Summary line",
            session_messages=(SessionMessage(role="user", content="Msg"),),
        )
        prompt = self._builder().build(ctx)
        summary_pos = prompt.content.index("Summary: Summary line")
        message_pos = prompt.content.index("user: Msg")
        assert summary_pos < message_pos

    def test_session_message_order_preserved(self) -> None:
        ctx = self._make_context(
            session_messages=(
                SessionMessage(role="user", content="First"),
                SessionMessage(role="assistant", content="Second"),
            ),
        )
        prompt = self._builder().build(ctx)
        first_pos = prompt.content.index("user: First")
        second_pos = prompt.content.index("assistant: Second")
        assert first_pos < second_pos

    def test_session_role_preserved(self) -> None:
        ctx = self._make_context(
            session_messages=(SessionMessage(role="CUSTOM_ROLE", content="Text"),),
        )
        prompt = self._builder().build(ctx)
        assert "CUSTOM_ROLE: Text" in prompt.content

    def test_session_content_preserved(self) -> None:
        ctx = self._make_context(
            session_messages=(SessionMessage(role="user", content="  raw content  "),),
        )
        prompt = self._builder().build(ctx)
        assert "user:   raw content  " in prompt.content

    def test_budgeted_context_not_mutated(self) -> None:
        ctx = self._make_context(
            knowledge_items=(KnowledgeItem(text="K", source="d"),),
            memory_entries=(MemoryEntry(content="M"),),
            session_summary="S",
            session_messages=(SessionMessage(role="user", content="Hi"),),
        )
        before = copy.deepcopy(ctx)
        self._builder().build(ctx)
        assert ctx == before

    def test_identical_input_produces_identical_prompt(self) -> None:
        ctx = self._make_context(
            knowledge_items=(KnowledgeItem(text="K", source="d"),),
        )
        builder = self._builder()
        first = builder.build(ctx)
        second = builder.build(ctx)
        assert first.content == second.content
        assert first.version == second.version
        assert first.to_dict() == second.to_dict()

    def test_final_prompt_within_total_budget_accepted(self) -> None:
        ctx = self._make_context(effective_query="hi")
        prompt = self._builder().build(ctx)
        assert len(prompt.content) <= ctx.metadata.total_budget

    def test_final_prompt_above_total_budget_rejected(self) -> None:
        effective_query = "hello"
        content = f"[QUERY]\n{effective_query}"
        ctx = self._make_context(
            effective_query=effective_query,
            total_budget=len(content) - 1,
        )
        with pytest.raises(PromptValidationError) as exc_info:
            self._builder().build(ctx)
        assert "final prompt tokens" in str(exc_info.value)

    def test_builder_does_not_silently_truncate_on_overflow(self) -> None:
        long_query = "x" * 100
        ctx = self._make_context(
            effective_query=long_query,
            total_budget=10,
        )
        with pytest.raises(PromptValidationError):
            self._builder().build(ctx)

    def test_invalid_input_type_rejected(self) -> None:
        with pytest.raises(PromptValidationError):
            self._builder().build("not context")  # type: ignore[arg-type]

    def test_empty_effective_query_rejected(self) -> None:
        ctx = self._make_context(effective_query="")
        with pytest.raises(PromptValidationError):
            self._builder().build(ctx)

    def test_whitespace_effective_query_rejected(self) -> None:
        ctx = self._make_context(effective_query="   ")
        with pytest.raises(PromptValidationError):
            self._builder().build(ctx)

    def test_returns_prompt_instance(self) -> None:
        ctx = self._make_context()
        prompt = self._builder().build(ctx)
        assert isinstance(prompt, Prompt)

    def test_query_text_may_appear_in_knowledge_without_conflict(self) -> None:
        query = "What is Python?"
        ctx = self._make_context(
            knowledge_items=(KnowledgeItem(text=query, source="doc"),),
            effective_query=query,
        )
        prompt = self._builder().build(ctx)
        assert prompt.content.count(query) == 2
