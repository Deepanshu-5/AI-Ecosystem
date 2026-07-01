"""
tests/retriever/test_knowledge_retriever.py

Component tests for KnowledgeRetriever.
"""

import pytest

from retriever.knowledge_context import KnowledgeContext, KnowledgeItem
from retriever.knowledge_retriever import KnowledgeRetriever


class TestKnowledgeRetriever:
    def _make_retriever(self, items: list[KnowledgeItem]) -> KnowledgeRetriever:
        def search_fn(query: str) -> list[KnowledgeItem]:
            return list(items)

        return KnowledgeRetriever(search_fn=search_fn)

    def test_retrieve_with_results(self) -> None:
        items = [
            KnowledgeItem(text="Fact A", source="doc1.pdf", score=0.95),
            KnowledgeItem(text="Fact B", source="doc2.pdf", score=0.88),
        ]
        retriever = self._make_retriever(items)
        ctx = retriever.retrieve("test query")

        assert isinstance(ctx, KnowledgeContext)
        assert len(ctx.items) == 2
        assert ctx.items[0].text == "Fact A"
        assert ctx.metadata["query"] == "test query"
        assert ctx.metadata["item_count"] == 2

    def test_retrieve_empty(self) -> None:
        retriever = self._make_retriever([])
        ctx = retriever.retrieve("test query")

        assert isinstance(ctx, KnowledgeContext)
        assert len(ctx.items) == 0
        assert ctx.metadata["item_count"] == 0

    def test_retrieve_deterministic(self) -> None:
        items = [KnowledgeItem(text="Fact A", source="doc1.pdf")]
        retriever = self._make_retriever(items)
        ctx1 = retriever.retrieve("same query")
        ctx2 = retriever.retrieve("same query")
        assert ctx1 == ctx2

    def test_search_fn_receives_query(self) -> None:
        received_queries: list[str] = []

        def search_fn(query: str) -> list[KnowledgeItem]:
            received_queries.append(query)
            return []

        retriever = KnowledgeRetriever(search_fn=search_fn)
        retriever.retrieve("specific query")
        assert received_queries == ["specific query"]

    def test_no_side_effects(self) -> None:
        retriever = self._make_retriever([])
        ctx = retriever.retrieve("query")
        # Calling again should be independent
        ctx2 = retriever.retrieve("query")
        assert ctx == ctx2
