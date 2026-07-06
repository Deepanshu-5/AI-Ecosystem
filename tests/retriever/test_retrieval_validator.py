"""
tests/retriever/test_retrieval_validator.py

Validator tests for RetrievalValidator.
"""

import pytest

from retriever.exceptions import RetrievalValidationError, UnsupportedSchemaVersionError
from retriever.knowledge_context import KnowledgeContext, KnowledgeItem
from retriever.memory_context import MemoryContext, MemoryEntry
from retriever.retrieval_metadata import RetrievalMetadata
from retriever.retrieved_context import RetrievedContext
from retriever.retrieval_validator import RetrievalValidator
from retriever.session_context import SessionContext, SessionMessage


class TestRetrievalValidator:
    def _make_valid_context(self) -> RetrievedContext:
        return RetrievedContext(
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
            metadata=RetrievalMetadata(
                knowledge_count=1,
                memory_count=1,
                session_count=1,
                knowledge_latency_ms=10,
                memory_latency_ms=5,
                session_latency_ms=3,
                total_latency_ms=18,
               
            ),
        )

    def test_valid_context_passes(self) -> None:
        ctx = self._make_valid_context()
        RetrievalValidator.validate(ctx)  # should not raise

    def test_empty_context_passes(self) -> None:
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
            schema_version=1,
            ),
        )
        RetrievalValidator.validate(ctx)  # should not raise

    def test_invalid_type_fails(self) -> None:
        with pytest.raises(RetrievalValidationError) as exc_info:
            RetrievalValidator.validate("not a context")  # type: ignore[arg-type]
        assert "expected RetrievedContext" in str(exc_info.value)

    def test_wrong_knowledge_type_fails(self) -> None:
        ctx = RetrievedContext(
            knowledge="not a context",  # type: ignore[arg-type]
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
        with pytest.raises(RetrievalValidationError) as exc_info:
            RetrievalValidator.validate(ctx)
        assert "expected KnowledgeContext" in str(exc_info.value)

    def test_wrong_memory_type_fails(self) -> None:
        ctx = RetrievedContext(
            knowledge=KnowledgeContext(items=(), metadata={}),
            memory="not a context",  # type: ignore[arg-type]
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
        with pytest.raises(RetrievalValidationError) as exc_info:
            RetrievalValidator.validate(ctx)
        assert "expected MemoryContext" in str(exc_info.value)

    def test_wrong_session_type_fails(self) -> None:
        ctx = RetrievedContext(
            knowledge=KnowledgeContext(items=(), metadata={}),
            memory=MemoryContext(entries=(), metadata={}),
            session="not a context",  # type: ignore[arg-type]
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
        with pytest.raises(RetrievalValidationError) as exc_info:
            RetrievalValidator.validate(ctx)
        assert "expected SessionContext" in str(exc_info.value)

    def test_version_less_than_one_fails(self) -> None:
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
            version=0,
        )
        with pytest.raises(RetrievalValidationError) as exc_info:
            RetrievalValidator.validate(ctx)
        assert "must be >= 1" in str(exc_info.value)

    def test_unsupported_version_fails(self) -> None:
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
            schema_version=1,
            ),
            version=999,
        )
        with pytest.raises(RetrievalValidationError) as exc_info:
            RetrievalValidator.validate(ctx)
        assert "999" in str(exc_info.value)

    def test_negative_count_fails(self) -> None:
        ctx = RetrievedContext(
            knowledge=KnowledgeContext(items=(), metadata={}),
            memory=MemoryContext(entries=(), metadata={}),
            session=SessionContext(summary="", recent_messages=(), metadata={}),
            metadata=RetrievalMetadata(
                knowledge_count=-1,
                memory_count=0,
                session_count=0,
                knowledge_latency_ms=0,
                memory_latency_ms=0,
                session_latency_ms=0,
                total_latency_ms=0,
            schema_version=1,
            ),
        )
        with pytest.raises(RetrievalValidationError) as exc_info:
            RetrievalValidator.validate(ctx)
        assert "must be >= 0" in str(exc_info.value)

    def test_negative_latency_fails(self) -> None:
        ctx = RetrievedContext(
            knowledge=KnowledgeContext(items=(), metadata={}),
            memory=MemoryContext(entries=(), metadata={}),
            session=SessionContext(summary="", recent_messages=(), metadata={}),
            metadata=RetrievalMetadata(
                knowledge_count=0,
                memory_count=0,
                session_count=0,
                knowledge_latency_ms=-1,
                memory_latency_ms=0,
                session_latency_ms=0,
                total_latency_ms=0,
                
            ),
        )
        with pytest.raises(RetrievalValidationError) as exc_info:
            RetrievalValidator.validate(ctx)
        assert "must be >= 0" in str(exc_info.value)

    def test_count_mismatch_fails(self) -> None:
        ctx = RetrievedContext(
            knowledge=KnowledgeContext(
                items=(KnowledgeItem(text="A", source="doc"),),
                metadata={},
            ),
            memory=MemoryContext(entries=(), metadata={}),
            session=SessionContext(summary="", recent_messages=(), metadata={}),
            metadata=RetrievalMetadata(
                knowledge_count=5,
                memory_count=0,
                session_count=0,
                knowledge_latency_ms=0,
                memory_latency_ms=0,
                session_latency_ms=0,
                total_latency_ms=0,
            schema_version=1,
            ),
        )
        with pytest.raises(RetrievalValidationError) as exc_info:
            RetrievalValidator.validate(ctx)
        assert "does not match actual knowledge item count" in str(exc_info.value)

    def test_multiple_violations_reported_together(self) -> None:
        ctx = RetrievedContext(
            knowledge="bad",  # type: ignore[arg-type]
            memory="bad",  # type: ignore[arg-type]
            session="bad",  # type: ignore[arg-type]
            metadata="bad",  # type: ignore[arg-type]
            version="bad",  # type: ignore[arg-type]
        )
        with pytest.raises(RetrievalValidationError) as exc_info:
            RetrievalValidator.validate(ctx)
        error_msg = str(exc_info.value)
        assert "expected KnowledgeContext" in error_msg
        assert "expected MemoryContext" in error_msg
        assert "expected SessionContext" in error_msg

    def test_deterministic_validation(self) -> None:
        ctx = self._make_valid_context()
        # Validation should be deterministic and side-effect-free
        RetrievalValidator.validate(ctx)
        RetrievalValidator.validate(ctx)
        RetrievalValidator.validate(ctx)
