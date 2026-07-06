"""
tests/budgeting/test_budget_validator.py

Unit tests for BudgetValidator.
"""

from __future__ import annotations

import pytest

from budgeting.budget_metadata import BudgetMetadata
from budgeting.budget_validator import BudgetValidator
from budgeting.budgeted_context import BudgetedContext
from budgeting.exceptions import ContextBudgetValidationError
from retriever.knowledge_context import KnowledgeContext, KnowledgeItem
from retriever.memory_context import MemoryContext, MemoryEntry
from retriever.retrieval_metadata import RetrievalMetadata
from retriever.retrieved_context import RetrievedContext
from retriever.session_context import SessionContext, SessionMessage


class TestBudgetValidatorInput:
    def _make_context(self) -> RetrievedContext:
        return RetrievedContext(
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

    def test_valid_input_passes(self) -> None:
        ctx = self._make_context()
        BudgetValidator.validate_input(ctx, "query", 1000, 200, None)

    def test_non_retrieved_context_fails(self) -> None:
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_input("not context", "query", 1000, 200, None)
        assert "expected RetrievedContext" in str(exc_info.value)

    def test_non_string_query_fails(self) -> None:
        ctx = self._make_context()
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_input(ctx, 123, 1000, 200, None)  # type: ignore[arg-type]
        assert "expected str" in str(exc_info.value)

    def test_empty_query_fails(self) -> None:
        ctx = self._make_context()
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_input(ctx, "", 1000, 200, None)
        assert "query: must not be empty" in str(exc_info.value)

    def test_whitespace_query_fails(self) -> None:
        ctx = self._make_context()
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_input(ctx, "   ", 1000, 200, None)
        assert "query: must not be empty" in str(exc_info.value)

    def test_non_positive_total_budget_fails(self) -> None:
        ctx = self._make_context()
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_input(ctx, "query", 0, 200, None)
        assert "total_budget" in str(exc_info.value)

    def test_negative_total_budget_fails(self) -> None:
        ctx = self._make_context()
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_input(ctx, "query", -1, 200, None)
        assert "total_budget" in str(exc_info.value)

    def test_negative_reserved_budget_fails(self) -> None:
        ctx = self._make_context()
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_input(ctx, "query", 1000, -1, None)
        assert "reserved_budget" in str(exc_info.value)

    def test_reserved_equals_total_fails(self) -> None:
        ctx = self._make_context()
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_input(ctx, "query", 1000, 1000, None)
        assert "reserved_budget" in str(exc_info.value)

    def test_reserved_greater_than_total_fails(self) -> None:
        ctx = self._make_context()
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_input(ctx, "query", 1000, 1200, None)
        assert "reserved_budget" in str(exc_info.value)

    def test_multiple_violations_reported(self) -> None:
        ctx = self._make_context()
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_input(ctx, "", 0, 1000, None)
        error = str(exc_info.value)
        assert "query" in error
        assert "total_budget" in error
        assert "reserved_budget" in error


class TestBudgetValidatorCategoryCaps:
    def test_valid_caps_pass(self) -> None:
        caps = {"knowledge": 0.6, "memory": 0.25, "session": 0.15}
        BudgetValidator.validate_input(
            RetrievedContext(
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
            ),
            "query",
            1000,
            200,
            caps,
        )

    def test_missing_key_fails(self) -> None:
        caps = {"knowledge": 0.6, "memory": 0.4}
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
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_input(ctx, "query", 1000, 200, caps)
        assert "must contain exactly" in str(exc_info.value)

    def test_non_numeric_cap_fails(self) -> None:
        caps = {"knowledge": "0.6", "memory": 0.25, "session": 0.15}  # type: ignore[dict-item]
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
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_input(ctx, "query", 1000, 200, caps)
        assert "must be numeric" in str(exc_info.value)

    def test_negative_cap_fails(self) -> None:
        caps = {"knowledge": -0.1, "memory": 0.25, "session": 0.85}
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
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_input(ctx, "query", 1000, 200, caps)
        assert "must be non-negative" in str(exc_info.value)

    def test_caps_not_total_one_fails(self) -> None:
        caps = {"knowledge": 0.5, "memory": 0.25, "session": 0.15}
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
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_input(ctx, "query", 1000, 200, caps)
        assert "must total exactly 1.0" in str(exc_info.value)


class TestBudgetValidatorOutput:
    def _make_budgeted(self, **overrides: object) -> BudgetedContext:
        meta = BudgetMetadata(
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
        # Apply overrides
        meta_dict = meta.to_dict()
        meta_dict.update(overrides)
        meta = BudgetMetadata(**meta_dict)  # type: ignore[arg-type]
        return BudgetedContext(
            knowledge=KnowledgeContext(items=(), metadata={}),
            memory=MemoryContext(entries=(), metadata={}),
            session=SessionContext(summary="", recent_messages=(), metadata={}),
            metadata=meta,
            effective_query="test",
        )

    def test_valid_output_passes(self) -> None:
        budgeted = self._make_budgeted()
        BudgetValidator.validate_output(budgeted, 750, 1000)

    def test_used_exceeds_context_budget_fails(self) -> None:
        budgeted = self._make_budgeted(used_context_tokens=800)
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_output(budgeted, 750, 1000)
        assert "exceeds context_budget" in str(exc_info.value)

    def test_total_usage_exceeds_total_budget_fails(self) -> None:
        budgeted = self._make_budgeted(
            reserved_tokens=200,
            query_tokens=100,
            used_context_tokens=800,
        )
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_output(budgeted, 700, 1000)
        assert "exceeds total_budget" in str(exc_info.value)

    def test_negative_remaining_fails(self) -> None:
        budgeted = self._make_budgeted(remaining_tokens=-1)
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_output(budgeted, 750, 1000)
        assert "negative" in str(exc_info.value)

    def test_negative_category_tokens_fails(self) -> None:
        budgeted = self._make_budgeted(knowledge_tokens=-1)
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_output(budgeted, 750, 1000)
        assert "knowledge_tokens" in str(exc_info.value)

    def test_category_sum_mismatch_fails(self) -> None:
        budgeted = self._make_budgeted(
            knowledge_tokens=100,
            memory_tokens=80,
            session_tokens=20,
            used_context_tokens=250,
        )
        with pytest.raises(ContextBudgetValidationError) as exc_info:
            BudgetValidator.validate_output(budgeted, 750, 1000)
        assert "does not equal" in str(exc_info.value)
