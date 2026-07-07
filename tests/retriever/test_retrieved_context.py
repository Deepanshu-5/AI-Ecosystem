"""
tests/retriever/test_retrieved_context.py

Unit tests for RetrievedContext.
"""

import pytest

from retriever.knowledge_context import KnowledgeContext, KnowledgeItem
from retriever.memory_context import MemoryContext, MemoryEntry
from retriever.retrieval_metadata import RetrievalMetadata
from retriever.retrieved_context import CURRENT_SCHEMA_VERSION, RetrievedContext
from retriever.session_context import SessionContext, SessionMessage


class TestRetrievedContext:
    def test_creation(self) -> None:
        knowledge = KnowledgeContext(
            items=(KnowledgeItem(text="Fact", source="doc"),),
            metadata={},
        )
        memory = MemoryContext(
            entries=(MemoryEntry(content="Preference"),),
            metadata={},
        )
        session = SessionContext(
            summary="Summary",
            recent_messages=(SessionMessage(role="user", content="Hi"),),
            metadata={},
        )
        metadata = RetrievalMetadata(
            knowledge_count=1,
            memory_count=1,
            session_count=1,
            knowledge_latency_ms=10,
            memory_latency_ms=5,
            session_latency_ms=3,
            total_latency_ms=18,
        )

        ctx = RetrievedContext(
            knowledge=knowledge,
            memory=memory,
            session=session,
            metadata=metadata,
        )

        assert ctx.knowledge == knowledge
        assert ctx.memory == memory
        assert ctx.session == session
        assert ctx.metadata == metadata
        assert ctx.version == CURRENT_SCHEMA_VERSION

    def test_default_version(self) -> None:
        ctx = RetrievedContext(
            knowledge=KnowledgeContext(items=(), metadata={}),
            memory=MemoryContext(entries=(), metadata={}),
            session=SessionContext(summary="", recent_messages=(), metadata={}),
            metadata=RetrievalMetadata(
                knowledge_count=0,
                memory_count=0,
                session_count=0,
                knowledge_latency_ms=0,
                memory_latency_ms=0,
                session_latency_ms=0,
                total_latency_ms=0,
                
            ),
        )
        assert ctx.version == CURRENT_SCHEMA_VERSION

    def test_immutability(self) -> None:
        ctx = RetrievedContext(
            knowledge=KnowledgeContext(items=(), metadata={}),
            memory=MemoryContext(entries=(), metadata={}),
            session=SessionContext(summary="", recent_messages=(), metadata={}),
            metadata=RetrievalMetadata(
                knowledge_count=0,
                memory_count=0,
                session_count=0,
                knowledge_latency_ms=0,
                memory_latency_ms=0,
                session_latency_ms=0,
                total_latency_ms=0,
            ),
        )
        with pytest.raises(AttributeError):
            ctx.version = 99  # type: ignore[misc]

    def test_to_dict(self) -> None:
        ctx = RetrievedContext(
            knowledge=KnowledgeContext(items=(), metadata={}),
            memory=MemoryContext(entries=(), metadata={}),
            session=SessionContext(summary="", recent_messages=(), metadata={}),
            metadata=RetrievalMetadata(
                knowledge_count=0,
                memory_count=0,
                session_count=0,
                knowledge_latency_ms=0,
                memory_latency_ms=0,
                session_latency_ms=0,
                total_latency_ms=0,
            ),
        )
        d = ctx.to_dict()
        assert "knowledge" in d
        assert "memory" in d
        assert "session" in d
        assert "metadata" in d
        assert "version" in d
        assert d["version"] == CURRENT_SCHEMA_VERSION
