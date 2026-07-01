"""
tests/retriever/test_memory_retriever.py

Component tests for MemoryRetriever.
"""

import pytest

from retriever.memory_context import MemoryContext, MemoryEntry
from retriever.memory_retriever import MemoryRetriever


class TestMemoryRetriever:
    def _make_retriever(self, entries: list[MemoryEntry]) -> MemoryRetriever:
        def search_fn(query: str) -> list[MemoryEntry]:
            return list(entries)

        return MemoryRetriever(search_fn=search_fn)

    def test_retrieve_with_results(self) -> None:
        entries = [
            MemoryEntry(content="Likes blue", memory_id="m1", score=0.9),
            MemoryEntry(content="Uses Python", memory_id="m2", score=0.85),
        ]
        retriever = self._make_retriever(entries)
        ctx = retriever.retrieve("test query")

        assert isinstance(ctx, MemoryContext)
        assert len(ctx.entries) == 2
        assert ctx.entries[0].content == "Likes blue"
        assert ctx.metadata["query"] == "test query"
        assert ctx.metadata["entry_count"] == 2

    def test_retrieve_empty(self) -> None:
        retriever = self._make_retriever([])
        ctx = retriever.retrieve("test query")

        assert isinstance(ctx, MemoryContext)
        assert len(ctx.entries) == 0
        assert ctx.metadata["entry_count"] == 0

    def test_retrieve_deterministic(self) -> None:
        entries = [MemoryEntry(content="Likes blue")]
        retriever = self._make_retriever(entries)
        ctx1 = retriever.retrieve("same query")
        ctx2 = retriever.retrieve("same query")
        assert ctx1 == ctx2

    def test_search_fn_receives_query(self) -> None:
        received_queries: list[str] = []

        def search_fn(query: str) -> list[MemoryEntry]:
            received_queries.append(query)
            return []

        retriever = MemoryRetriever(search_fn=search_fn)
        retriever.retrieve("specific query")
        assert received_queries == ["specific query"]
