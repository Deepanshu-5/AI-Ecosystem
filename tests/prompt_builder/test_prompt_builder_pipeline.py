"""
tests/prompt_builder/test_prompt_builder_pipeline.py

Cross-layer tests: RetrievedContext → ContextBudgeter → BudgetedContext → PromptBuilder → Prompt.
"""

from __future__ import annotations

import copy

import pytest

from budgeting.context_budgeter import ContextBudgeter
from prompt_builder.exceptions import PromptValidationError
from prompt_builder.prompt_builder import PromptBuilder
from retriever.knowledge_context import KnowledgeContext, KnowledgeItem
from retriever.memory_context import MemoryContext, MemoryEntry
from retriever.retrieval_metadata import RetrievalMetadata
from retriever.retrieved_context import RetrievedContext
from retriever.session_context import SessionContext, SessionMessage


class TestPromptBuilderPipeline:
    def _make_counter(self) -> tuple[ContextBudgeter, PromptBuilder]:
        def count(text: str) -> int:
            return len(text)

        def truncate(text: str, max_tokens: int) -> str:
            return text[:max_tokens]

        budgeter = ContextBudgeter(token_counter=count, token_truncator=truncate)
        builder = PromptBuilder(token_counter=count)
        return budgeter, builder

    def _make_retrieved_context(
        self,
        knowledge_items: tuple[KnowledgeItem, ...] = (),
        memory_entries: tuple[MemoryEntry, ...] = (),
        session_summary: str = "",
        session_messages: tuple[SessionMessage, ...] = (),
    ) -> RetrievedContext:
        return RetrievedContext(
            knowledge=KnowledgeContext(items=knowledge_items, metadata={}),
            memory=MemoryContext(entries=memory_entries, metadata={}),
            session=SessionContext(
                summary=session_summary,
                recent_messages=session_messages,
                metadata={},
            ),
            metadata=RetrievalMetadata(
                knowledge_count=len(knowledge_items),
                memory_count=len(memory_entries),
                session_count=len(session_messages),
                knowledge_latency_ms=0,
                memory_latency_ms=0,
                session_latency_ms=0,
                total_latency_ms=0,
            ),
        )

    def test_budgeted_knowledge_reaches_prompt_in_order(self) -> None:
        budgeter, builder = self._make_counter()
        retrieved = self._make_retrieved_context(
            knowledge_items=(
                KnowledgeItem(text="FactA", source="doc1"),
                KnowledgeItem(text="FactB", source="doc2"),
            ),
        )
        budgeted = budgeter.budget(retrieved, "hi", total_budget=200, reserved_budget=20)
        prompt = builder.build(budgeted)

        assert "[KNOWLEDGE]\nFactA\nFactB" in prompt.content
        assert "doc1" not in prompt.content
        assert "doc2" not in prompt.content

    def test_budgeted_memory_reaches_prompt_in_order(self) -> None:
        budgeter, builder = self._make_counter()
        retrieved = self._make_retrieved_context(
            memory_entries=(
                MemoryEntry(content="PrefA"),
                MemoryEntry(content="PrefB"),
            ),
        )
        budgeted = budgeter.budget(retrieved, "hi", total_budget=200, reserved_budget=20)
        prompt = builder.build(budgeted)

        assert "[MEMORY]\nPrefA\nPrefB" in prompt.content

    def test_budgeted_session_reaches_prompt_in_order(self) -> None:
        budgeter, builder = self._make_counter()
        retrieved = self._make_retrieved_context(
            session_summary="Summary text",
            session_messages=(
                SessionMessage(role="user", content="Hello"),
                SessionMessage(role="assistant", content="Hi"),
            ),
        )
        budgeted = budgeter.budget(retrieved, "hi", total_budget=500, reserved_budget=20)
        prompt = builder.build(budgeted)

        assert "Summary: Summary text" in prompt.content
        assert "user: Hello" in prompt.content
        assert "assistant: Hi" in prompt.content
        summary_pos = prompt.content.index("Summary: Summary text")
        user_pos = prompt.content.index("user: Hello")
        assistant_pos = prompt.content.index("assistant: Hi")
        assert summary_pos < user_pos < assistant_pos

    def test_truncated_effective_query_is_prompt_query(self) -> None:
        budgeter, builder = self._make_counter()
        long_query = "A" * 200
        retrieved = self._make_retrieved_context()
        budgeted = budgeter.budget(
            retrieved,
            long_query,
            total_budget=100,
            reserved_budget=30,
        )
        prompt = builder.build(budgeted)

        assert budgeted.metadata.query_truncated is True
        assert budgeted.effective_query != long_query
        assert prompt.content.endswith(budgeted.effective_query)
        assert f"[QUERY]\n{budgeted.effective_query}" in prompt.content
        assert long_query not in prompt.content

    def test_omitted_budgeter_context_does_not_reappear(self) -> None:
        budgeter, builder = self._make_counter()
        retrieved = self._make_retrieved_context(
            knowledge_items=(
                KnowledgeItem(text="A" * 100, source="doc1"),
                KnowledgeItem(text="B" * 100, source="doc2"),
            ),
        )
        budgeted = budgeter.budget(retrieved, "hi", total_budget=80, reserved_budget=25)
        prompt = builder.build(budgeted)

        assert len(budgeted.knowledge.items) <= 2
        assert len(budgeted.knowledge.items) >= 1
        for item in budgeted.knowledge.items:
            assert item.text in prompt.content
        omitted = [
            item.text
            for item in retrieved.knowledge.items
            if item not in budgeted.knowledge.items
        ]
        for text in omitted:
            assert text not in prompt.content

    def test_prompt_builder_does_not_modify_budgeted_context(self) -> None:
        budgeter, builder = self._make_counter()
        retrieved = self._make_retrieved_context(
            knowledge_items=(KnowledgeItem(text="Fact", source="doc"),),
            memory_entries=(MemoryEntry(content="Pref"),),
            session_summary="Summary",
            session_messages=(SessionMessage(role="user", content="Hi"),),
        )
        budgeted = budgeter.budget(retrieved, "hello", total_budget=500, reserved_budget=50)
        before = copy.deepcopy(budgeted)
        builder.build(budgeted)
        assert budgeted == before

    def test_exact_final_prompt_respects_total_budget(self) -> None:
        budgeter, builder = self._make_counter()
        retrieved = self._make_retrieved_context(
            knowledge_items=(KnowledgeItem(text="Fact", source="doc"),),
            memory_entries=(MemoryEntry(content="Pref"),),
            session_summary="Summary",
            session_messages=(SessionMessage(role="user", content="Hi"),),
        )
        budgeted = budgeter.budget(retrieved, "hello", total_budget=500, reserved_budget=50)
        prompt = builder.build(budgeted)

        assert len(prompt.content) <= budgeted.metadata.total_budget

    def test_insufficient_reservation_produces_explicit_validation_failure(self) -> None:
        budgeter, builder = self._make_counter()
        retrieved = self._make_retrieved_context()
        budgeted = budgeter.budget(
            retrieved,
            "hello",
            total_budget=10,
            reserved_budget=5,
        )

        with pytest.raises(PromptValidationError) as exc_info:
            builder.build(budgeted)
        assert "final prompt tokens" in str(exc_info.value)
        assert "exceed total_budget" in str(exc_info.value)

    def test_repeated_cross_layer_execution_is_deterministic(self) -> None:
        budgeter, builder = self._make_counter()
        retrieved = self._make_retrieved_context(
            knowledge_items=(KnowledgeItem(text="Fact", source="doc"),),
            memory_entries=(MemoryEntry(content="Pref"),),
            session_summary="Summary",
            session_messages=(SessionMessage(role="user", content="Hi"),),
        )
        budgeted = budgeter.budget(retrieved, "hello", total_budget=500, reserved_budget=50)

        first = builder.build(budgeted)
        second = builder.build(budgeted)

        assert first.content == second.content
        assert first.to_dict() == second.to_dict()
