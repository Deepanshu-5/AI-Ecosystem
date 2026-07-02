"""
tests/retriever/test_retrieval_metadata.py

Unit tests for RetrievalMetadata.
"""

import pytest

from retriever.retrieval_metadata import RetrievalMetadata


class TestRetrievalMetadata:
    def test_creation(self) -> None:
        meta = RetrievalMetadata(
            knowledge_count=2,
            memory_count=1,
            session_count=3,
            knowledge_latency_ms=100,
            memory_latency_ms=50,
            session_latency_ms=30,
            total_latency_ms=180,
           
        )
        assert meta.knowledge_count == 2
        assert meta.total_latency_ms == 180

    def test_immutability(self) -> None:
        meta = RetrievalMetadata(
            knowledge_count=0,
            memory_count=0,
            session_count=0,
            knowledge_latency_ms=0,
            memory_latency_ms=0,
            session_latency_ms=0,
            total_latency_ms=0,
            
        )
        with pytest.raises(AttributeError):
            meta.knowledge_count = 5  # type: ignore[misc]

    def test_to_dict(self) -> None:
        meta = RetrievalMetadata(
            knowledge_count=2,
            memory_count=1,
            session_count=3,
            knowledge_latency_ms=100,
            memory_latency_ms=50,
            session_latency_ms=30,
            total_latency_ms=180,
            
        )
        d = meta.to_dict()
        assert d["knowledge_count"] == 2
        assert d["total_latency_ms"] == 180

    def test_zero_values(self) -> None:
        meta = RetrievalMetadata(
            knowledge_count=0,
            memory_count=0,
            session_count=0,
            knowledge_latency_ms=0,
            memory_latency_ms=0,
            session_latency_ms=0,
            total_latency_ms=0,
            
        )
        assert meta.knowledge_count == 0
        assert meta.total_latency_ms == 0
