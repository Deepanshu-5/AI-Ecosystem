"""
tests/budgeting/test_budgeted_context.py

Unit tests for BudgetedContext.
"""

import pytest

from budgeting.budget_metadata import BudgetMetadata
from budgeting.budgeted_context import BudgetedContext
from retriever.knowledge_context import KnowledgeContext, KnowledgeItem
from retriever.memory_context import MemoryContext, MemoryEntry
from retriever.session_context import SessionContext, SessionMessage


class TestBudgetedContext:
    def _make_meta(self) -> BudgetMetadata:
        return BudgetMetadata(
            total_budget=1000,
            reserved_tokens=200,
            query_tokens=50,
            context_budget=750,
            used_context_tokens=300,
            remaining_tokens=450,
            knowledge_tokens=200,
            memory_tokens=80,
            session_tokens=20,
        )

    def test_creation(self) -> None:
        ctx = BudgetedContext(
            knowledge=KnowledgeContext(
                items=(KnowledgeItem(text="Fact", source="doc"),),
                metadata={},
            ),
            memory=MemoryContext(
                entries=(MemoryEntry(content="Pref"),),
                metadata={},
            ),
            session=SessionContext(
                summary="Summary",
                recent_messages=(SessionMessage(role="user", content="Hi"),),
                metadata={},
            ),
            metadata=self._make_meta(),
            effective_query="hello",
        )
        assert ctx.effective_query == "hello"
        assert ctx.version == 1

    def test_default_version(self) -> None:
        ctx = BudgetedContext(
            knowledge=KnowledgeContext(items=(), metadata={}),
            memory=MemoryContext(entries=(), metadata={}),
            session=SessionContext(summary="", recent_messages=(), metadata={}),
            metadata=self._make_meta(),
            effective_query="",
        )
        assert ctx.version == 1

    def test_immutability(self) -> None:
        ctx = BudgetedContext(
            knowledge=KnowledgeContext(items=(), metadata={}),
            memory=MemoryContext(entries=(), metadata={}),
            session=SessionContext(summary="", recent_messages=(), metadata={}),
            metadata=self._make_meta(),
            effective_query="",
        )
        with pytest.raises(AttributeError):
            ctx.version = 99  # type: ignore[misc]

    def test_to_dict(self) -> None:
        ctx = BudgetedContext(
            knowledge=KnowledgeContext(items=(), metadata={}),
            memory=MemoryContext(entries=(), metadata={}),
            session=SessionContext(summary="", recent_messages=(), metadata={}),
            metadata=self._make_meta(),
            effective_query="test",
        )
        d = ctx.to_dict()
        assert "knowledge" in d
        assert "memory" in d
        assert "session" in d
        assert "metadata" in d
        assert "effective_query" in d
        assert "version" in d
        assert d["effective_query"] == "test"
        assert d["version"] == 1

    def test_empty_context(self) -> None:
        ctx = BudgetedContext(
            knowledge=KnowledgeContext(items=(), metadata={}),
            memory=MemoryContext(entries=(), metadata={}),
            session=SessionContext(summary="", recent_messages=(), metadata={}),
            metadata=self._make_meta(),
            effective_query="",
        )
        assert ctx.knowledge.items == ()
        assert ctx.memory.entries == ()
        assert ctx.session.recent_messages == ()
