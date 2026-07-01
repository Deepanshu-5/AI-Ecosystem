"""
tests/retriever/test_knowledge_context.py

Unit tests for KnowledgeItem and KnowledgeContext.
"""

import pytest

from retriever.knowledge_context import KnowledgeContext, KnowledgeItem


class TestKnowledgeItem:
    def test_creation(self) -> None:
        item = KnowledgeItem(text="Fact A", source="doc1.pdf", score=0.95)
        assert item.text == "Fact A"
        assert item.source == "doc1.pdf"
        assert item.score == 0.95

    def test_creation_without_score(self) -> None:
        item = KnowledgeItem(text="Fact B", source="doc2.pdf")
        assert item.score is None

    def test_immutability(self) -> None:
        item = KnowledgeItem(text="Fact A", source="doc1.pdf")
        with pytest.raises(AttributeError):
            item.text = "Modified"  # type: ignore[misc]

    def test_to_dict(self) -> None:
        item = KnowledgeItem(text="Fact A", source="doc1.pdf", score=0.95)
        d = item.to_dict()
        assert d == {"text": "Fact A", "source": "doc1.pdf", "score": 0.95}

    def test_to_dict_without_score(self) -> None:
        item = KnowledgeItem(text="Fact B", source="doc2.pdf")
        d = item.to_dict()
        assert d["score"] is None


class TestKnowledgeContext:
    def test_creation(self) -> None:
        item = KnowledgeItem(text="Fact A", source="doc1.pdf")
        ctx = KnowledgeContext(items=(item,), metadata={"key": "value"})
        assert len(ctx.items) == 1
        assert ctx.metadata == {"key": "value"}

    def test_empty_context(self) -> None:
        ctx = KnowledgeContext(items=(), metadata={})
        assert len(ctx.items) == 0

    def test_immutability(self) -> None:
        ctx = KnowledgeContext(items=(), metadata={})
        with pytest.raises(AttributeError):
            ctx.items = ()  # type: ignore[misc]

    def test_to_dict(self) -> None:
        item = KnowledgeItem(text="Fact A", source="doc1.pdf")
        ctx = KnowledgeContext(items=(item,), metadata={"count": 1})
        d = ctx.to_dict()
        assert d["items"] == [{"text": "Fact A", "source": "doc1.pdf", "score": None}]
        assert d["metadata"] == {"count": 1}

    def test_tuple_immutability(self) -> None:
        item = KnowledgeItem(text="Fact A", source="doc1.pdf")
        ctx = KnowledgeContext(items=(item,), metadata={})
        with pytest.raises((TypeError, AttributeError)):
            ctx.items += (KnowledgeItem(text="B", source="s"),)  # type: ignore[operator]
