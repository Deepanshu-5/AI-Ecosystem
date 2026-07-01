"""
tests/retriever/test_memory_context.py

Unit tests for MemoryEntry and MemoryContext.
"""

import pytest

from retriever.memory_context import MemoryContext, MemoryEntry


class TestMemoryEntry:
    def test_creation(self) -> None:
        entry = MemoryEntry(content="User likes blue", memory_id="m1", score=0.88)
        assert entry.content == "User likes blue"
        assert entry.memory_id == "m1"
        assert entry.score == 0.88

    def test_creation_without_optional_fields(self) -> None:
        entry = MemoryEntry(content="User likes blue")
        assert entry.memory_id is None
        assert entry.score is None

    def test_immutability(self) -> None:
        entry = MemoryEntry(content="User likes blue")
        with pytest.raises(AttributeError):
            entry.content = "Modified"  # type: ignore[misc]

    def test_to_dict(self) -> None:
        entry = MemoryEntry(content="User likes blue", memory_id="m1", score=0.88)
        d = entry.to_dict()
        assert d == {"content": "User likes blue", "memory_id": "m1", "score": 0.88}


class TestMemoryContext:
    def test_creation(self) -> None:
        entry = MemoryEntry(content="User likes blue")
        ctx = MemoryContext(entries=(entry,), metadata={"key": "value"})
        assert len(ctx.entries) == 1
        assert ctx.metadata == {"key": "value"}

    def test_empty_context(self) -> None:
        ctx = MemoryContext(entries=(), metadata={})
        assert len(ctx.entries) == 0

    def test_immutability(self) -> None:
        ctx = MemoryContext(entries=(), metadata={})
        with pytest.raises(AttributeError):
            ctx.entries = ()  # type: ignore[misc]

    def test_to_dict(self) -> None:
        entry = MemoryEntry(content="User likes blue")
        ctx = MemoryContext(entries=(entry,), metadata={"count": 1})
        d = ctx.to_dict()
        assert d["entries"] == [{"content": "User likes blue", "memory_id": None, "score": None}]
        assert d["metadata"] == {"count": 1}
