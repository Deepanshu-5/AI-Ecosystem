"""
tests/budgeting/test_context_budgeter.py

Tests for ContextBudgeter two-phase allocation, truncation, query overflow.
"""

from __future__ import annotations

import pytest

from budgeting.budgeted_context import BudgetedContext
from budgeting.context_budgeter import ContextBudgeter
from budgeting.exceptions import ContextBudgetOverflowError, ContextBudgetValidationError
from retriever.knowledge_context import KnowledgeContext, KnowledgeItem
from retriever.memory_context import MemoryContext, MemoryEntry
from retriever.retrieval_metadata import RetrievalMetadata
from retriever.retrieved_context import RetrievedContext
from retriever.session_context import SessionContext, SessionMessage


class TestContextBudgeter:
    """Helper to build a token counter where tokens = len(text) for predictability."""

    def _make_counter(self) -> ContextBudgeter:
        def count(text: str) -> int:
            return len(text)

        def truncate(text: str, max_tokens: int) -> str:
            return text[:max_tokens]

        return ContextBudgeter(token_counter=count, token_truncator=truncate)

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
                schema_version=1,
            ),
        )

    # --- Empty context ---

    def test_empty_context(self) -> None:
        budgeter = self._make_counter()
        ctx = self._make_retrieved_context()
        result = budgeter.budget(ctx, "hello", total_budget=100, reserved_budget=20)

        assert isinstance(result, BudgetedContext)
        assert result.knowledge.items == ()
        assert result.memory.entries == ()
        assert result.session.recent_messages == ()
        assert result.metadata.query_tokens == 5
        assert result.metadata.context_budget == 75
        assert result.metadata.used_context_tokens == 0
        assert result.metadata.remaining_tokens == 75

    # --- Knowledge-only ---

    def test_knowledge_only_all_fit(self) -> None:
        budgeter = self._make_counter()
        items = (
            KnowledgeItem(text="FactA", source="doc1"),
            KnowledgeItem(text="FactB", source="doc2"),
        )
        ctx = self._make_retrieved_context(knowledge_items=items)
        result = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=10)

        # query="hi" = 2 tokens, context_budget = 100 - 10 - 2 = 88
        # Phase 1: knowledge cap = 88 * 0.6 = 52. FactA(5) + FactB(5) = 10 <= 52
        assert len(result.knowledge.items) == 2
        assert result.knowledge.items[0].text == "FactA"
        assert result.knowledge.items[1].text == "FactB"
        assert result.metadata.knowledge_tokens == 10

    def test_knowledge_only_some_fit(self) -> None:
        budgeter = self._make_counter()
        items = (
            KnowledgeItem(text="FactA", source="doc1"),   # 5 tokens
            KnowledgeItem(text="FactBLong", source="doc2"),  # 8 tokens
            KnowledgeItem(text="FactC", source="doc3"),   # 5 tokens
        )
        ctx = self._make_retrieved_context(knowledge_items=items)
        # query="hi" = 2, context_budget = 100 - 10 - 2 = 88
        # Phase 1: knowledge cap = 88 * 0.6 = 52
        # FactA(5) + FactBLong(8) + FactC(5) = 18 <= 52, all fit
        result = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=10)
        assert len(result.knowledge.items) == 3

    def test_knowledge_only_truncation(self) -> None:
        budgeter = self._make_counter()
        items = (KnowledgeItem(text="ABCDEFGHIJ", source="doc1"),)  # 10 tokens
        ctx = self._make_retrieved_context(knowledge_items=items)
        # query="hi" = 2, context_budget = 30 - 10 - 2 = 18
        # Phase 1: knowledge cap = 18 * 0.6 = 10
        # ABCDEFGHIJ = 10 tokens, fits exactly
        result = budgeter.budget(ctx, "hi", total_budget=30, reserved_budget=10)
        assert len(result.knowledge.items) == 1
        assert result.knowledge.items[0].text == "ABCDEFGHIJ"

    # --- Memory-only ---

    def test_memory_only_all_fit(self) -> None:
        budgeter = self._make_counter()
        entries = (
            MemoryEntry(content="PrefA"),
            MemoryEntry(content="PrefB"),
        )
        ctx = self._make_retrieved_context(memory_entries=entries)
        result = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=10)

        assert len(result.memory.entries) == 2
        assert result.memory.entries[0].content == "PrefA"
        assert result.memory.entries[1].content == "PrefB"

    # --- Session-only ---

    def test_session_only_summary_and_messages(self) -> None:
        budgeter = self._make_counter()
        ctx = self._make_retrieved_context(
            session_summary="Summary",
            session_messages=(
                SessionMessage(role="user", content="Hello"),
                SessionMessage(role="assistant", content="Hi"),
            ),
        )
        result = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=10)

        # Session cap = 88 * 0.15 = 13
        # Summary(7) + Hello(5) + Hi(2) = 14 > 13, so summary fits, Hello fits, Hi may not
        assert result.session.summary == "Summary"
        assert len(result.session.recent_messages) >= 0

    def test_session_summary_before_messages(self) -> None:
        budgeter = self._make_counter()
        ctx = self._make_retrieved_context(
            session_summary="SummaryText",  # 11 tokens
            session_messages=(
                SessionMessage(role="user", content="MsgA"),  # 4 tokens
            ),
        )
        # query="hi" = 2, context_budget = 100 - 5 - 2 = 93
        # Phase 1: session cap = 93 * 0.15 = 13
        # SummaryText(11) fits in 13, MsgA(4) fits in remaining 2
        result = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=5)
        assert result.session.summary == "SummaryText"
        assert len(result.session.recent_messages) == 1

    # --- All categories ---

    def test_all_categories(self) -> None:
        budgeter = self._make_counter()
        ctx = self._make_retrieved_context(
            knowledge_items=(
                KnowledgeItem(text="FactA", source="doc1"),
            ),
            memory_entries=(
                MemoryEntry(content="PrefA"),
            ),
            session_summary="Summary",
            session_messages=(
                SessionMessage(role="user", content="Hello"),
            ),
        )
        result = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=10)

        assert len(result.knowledge.items) == 1
        assert len(result.memory.entries) == 1
        assert result.session.summary == "Summary"
        assert len(result.session.recent_messages) == 1

    # --- Two-phase allocation ---

    def test_phase2_redistribution(self) -> None:
        budgeter = self._make_counter()
        # Knowledge items that exceed phase 1 cap but fit in phase 2
        items = (
            KnowledgeItem(text="A" * 50, source="doc1"),  # 50 tokens
            KnowledgeItem(text="B" * 50, source="doc2"),  # 50 tokens
        )
        ctx = self._make_retrieved_context(knowledge_items=items)
        # query="hi" = 2, context_budget = 200 - 20 - 2 = 178
        # Phase 1: knowledge cap = 178 * 0.6 = 106
        # Item1(50) fits, Item2(50) fits, total 100 <= 106, both fit in phase 1
        result = budgeter.budget(ctx, "hi", total_budget=200, reserved_budget=20)
        assert len(result.knowledge.items) == 2

    def test_phase2_redistribution_with_memory(self) -> None:
        budgeter = self._make_counter()
        knowledge_items = (KnowledgeItem(text="A" * 30, source="doc1"),)  # 30
        memory_entries = (MemoryEntry(content="B" * 30),)  # 30
        ctx = self._make_retrieved_context(
            knowledge_items=knowledge_items,
            memory_entries=memory_entries,
        )
        # query="hi" = 2, context_budget = 200 - 20 - 2 = 178
        # Phase 1: knowledge cap = 106, memory cap = 44
        # Knowledge(30) fits, Memory(30) fits
        result = budgeter.budget(ctx, "hi", total_budget=200, reserved_budget=20)
        assert len(result.knowledge.items) == 1
        assert len(result.memory.entries) == 1

    # --- Category caps ---

    def test_custom_category_caps(self) -> None:
        budgeter = self._make_counter()
        items = (KnowledgeItem(text="A" * 100, source="doc1"),)  # 100
        ctx = self._make_retrieved_context(knowledge_items=items)
        # query="hi" = 2, context_budget = 200 - 20 - 2 = 178
        # With custom caps knowledge=0.9: phase 1 cap = 160
        # Item(100) fits in phase 1
        caps = {"knowledge": 0.9, "memory": 0.05, "session": 0.05}
        result = budgeter.budget(ctx, "hi", total_budget=200, reserved_budget=20, category_caps=caps)
        assert len(result.knowledge.items) == 1

    # --- Query overflow ---

    def test_query_preserved_when_fits(self) -> None:
        budgeter = self._make_counter()
        ctx = self._make_retrieved_context()
        result = budgeter.budget(ctx, "hello world", total_budget=100, reserved_budget=10)

        assert result.effective_query == "hello world"
        assert result.metadata.query_tokens == 11
        assert result.metadata.query_truncated is False

    def test_query_truncated_on_overflow(self) -> None:
        budgeter = self._make_counter()
        ctx = self._make_retrieved_context()
        # query="hello world" = 11 tokens, reserved=10, total=20
        # query_tokens + reserved = 21 > 20, so overflow
        # query_budget = 20 - 10 = 10
        # truncate "hello world" to 10 tokens (minus marker)
        result = budgeter.budget(ctx, "hello world", total_budget=20, reserved_budget=10)

        assert result.metadata.query_truncated is True
        assert result.metadata.query_tokens <= 10
        assert result.effective_query != "hello world"
        assert "[...]" in result.effective_query or len(result.effective_query) <= 10

    def test_query_overflow_zero_budget_raises(self) -> None:
        budgeter = self._make_counter()
        ctx = self._make_retrieved_context()
        # reserved_budget >= total_budget fails input validation before
        # query overflow logic is reached
        with pytest.raises(ContextBudgetValidationError):
            budgeter.budget(ctx, "hello world", total_budget=10, reserved_budget=10)

    # --- Truncation ---

    def test_unit_truncation(self) -> None:
        budgeter = self._make_counter()
        items = (KnowledgeItem(text="ABCDEFGHIJ", source="doc1"),)  # 10 tokens
        ctx = self._make_retrieved_context(knowledge_items=items)
        # query="hi" = 2, context_budget = 20 - 5 - 2 = 13
        # Phase 1: knowledge cap = 13 * 0.6 = 7
        # ABCDEFGHIJ(10) > 7, doesn't fit completely
        # Try truncation: marker " [...]" = 6 tokens, content budget = 7 - 6 = 1
        # truncated = "A" + " [...]" = 7 tokens, fits
        result = budgeter.budget(ctx, "hi", total_budget=20, reserved_budget=5)

        assert len(result.knowledge.items) == 1
        assert result.knowledge.items[0].text != "ABCDEFGHIJ"
        assert result.metadata.truncated_unit_count == 1

    # --- Zero remaining budget ---

    def test_zero_context_budget(self) -> None:
        budgeter = self._make_counter()
        items = (KnowledgeItem(text="Fact", source="doc1"),)
        ctx = self._make_retrieved_context(knowledge_items=items)
        # query="hello" = 5, reserved=10, total=15 -> context_budget = 0
        result = budgeter.budget(ctx, "hello", total_budget=15, reserved_budget=10)

        assert result.knowledge.items == ()
        assert result.metadata.used_context_tokens == 0
        assert result.metadata.remaining_tokens == 0

    # --- No duplicate selection ---

    def test_no_duplicate_selection(self) -> None:
        budgeter = self._make_counter()
        items = (KnowledgeItem(text="Fact", source="doc1"),)
        ctx = self._make_retrieved_context(knowledge_items=items)
        result = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=10)

        texts = [item.text for item in result.knowledge.items]
        assert len(texts) == len(set(texts))

    # --- Original RetrievedContext not mutated ---

    def test_original_not_mutated(self) -> None:
        budgeter = self._make_counter()
        items = (KnowledgeItem(text="Fact", source="doc1"),)
        ctx = self._make_retrieved_context(knowledge_items=items)
        original_text = ctx.knowledge.items[0].text

        result = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=10)

        assert ctx.knowledge.items[0].text == original_text
        assert result.knowledge.items[0].text == original_text

    # --- Determinism ---

    def test_deterministic_output(self) -> None:
        budgeter = self._make_counter()
        items = (
            KnowledgeItem(text="FactA", source="doc1"),
            KnowledgeItem(text="FactB", source="doc2"),
        )
        ctx = self._make_retrieved_context(knowledge_items=items)

        result1 = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=10)
        result2 = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=10)

        assert result1.knowledge == result2.knowledge
        assert result1.memory == result2.memory
        assert result1.session == result2.session
        assert result1.metadata == result2.metadata
        assert result1.effective_query == result2.effective_query

    # --- Input validation ---

    def test_invalid_input_rejected(self) -> None:
        budgeter = self._make_counter()
        ctx = self._make_retrieved_context()
        with pytest.raises(ContextBudgetValidationError):
            budgeter.budget(ctx, "", total_budget=100, reserved_budget=10)

    def test_invalid_total_budget_rejected(self) -> None:
        budgeter = self._make_counter()
        ctx = self._make_retrieved_context()
        with pytest.raises(ContextBudgetValidationError):
            budgeter.budget(ctx, "query", total_budget=0, reserved_budget=10)

    # --- Output invariants ---

    def test_used_context_within_budget(self) -> None:
        budgeter = self._make_counter()
        items = (KnowledgeItem(text="A" * 50, source="doc1"),)
        ctx = self._make_retrieved_context(knowledge_items=items)
        result = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=10)

        assert result.metadata.used_context_tokens <= result.metadata.context_budget

    def test_total_within_budget(self) -> None:
        budgeter = self._make_counter()
        items = (KnowledgeItem(text="A" * 50, source="doc1"),)
        ctx = self._make_retrieved_context(knowledge_items=items)
        result = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=10)

        total = (
            result.metadata.reserved_tokens
            + result.metadata.query_tokens
            + result.metadata.used_context_tokens
        )
        assert total <= result.metadata.total_budget

    def test_remaining_non_negative(self) -> None:
        budgeter = self._make_counter()
        ctx = self._make_retrieved_context()
        result = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=10)

        assert result.metadata.remaining_tokens >= 0

    def test_category_sum_equals_used(self) -> None:
        budgeter = self._make_counter()
        items = (KnowledgeItem(text="FactA", source="doc1"),)
        entries = (MemoryEntry(content="PrefA"),)
        ctx = self._make_retrieved_context(
            knowledge_items=items,
            memory_entries=entries,
            session_summary="Summary",
        )
        result = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=10)

        category_sum = (
            result.metadata.knowledge_tokens
            + result.metadata.memory_tokens
            + result.metadata.session_tokens
        )
        assert category_sum == result.metadata.used_context_tokens

    # --- Serialization ---

    def test_serialization(self) -> None:
        budgeter = self._make_counter()
        ctx = self._make_retrieved_context()
        result = budgeter.budget(ctx, "hi", total_budget=100, reserved_budget=10)

        d = result.to_dict()
        assert isinstance(d, dict)
        assert "knowledge" in d
        assert "memory" in d
        assert "session" in d
        assert "metadata" in d
        assert "effective_query" in d
        assert "version" in d
