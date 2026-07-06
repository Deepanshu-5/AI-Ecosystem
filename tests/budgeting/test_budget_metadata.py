"""
tests/budgeting/test_budget_metadata.py

Unit tests for BudgetMetadata.
"""

import pytest

from budgeting.budget_metadata import BudgetMetadata


class TestBudgetMetadata:
    def test_creation(self) -> None:
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
        assert meta.total_budget == 1000
        assert meta.query_truncated is False
        assert meta.truncated_unit_count == 0

    def test_with_truncation(self) -> None:
        meta = BudgetMetadata(
            total_budget=1000,
            reserved_tokens=200,
            query_tokens=30,
            context_budget=770,
            used_context_tokens=300,
            remaining_tokens=470,
            knowledge_tokens=200,
            memory_tokens=80,
            session_tokens=20,
            query_truncated=True,
            truncated_unit_count=2,
        )
        assert meta.query_truncated is True
        assert meta.truncated_unit_count == 2

    def test_immutability(self) -> None:
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
        with pytest.raises(AttributeError):
            meta.total_budget = 500  # type: ignore[misc]

    def test_to_dict(self) -> None:
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
            query_truncated=True,
            truncated_unit_count=1,
        )
        d = meta.to_dict()
        assert d["total_budget"] == 1000
        assert d["query_truncated"] is True
        assert d["truncated_unit_count"] == 1
        assert "used_context_tokens" in d

    def test_zero_values(self) -> None:
        meta = BudgetMetadata(
            total_budget=100,
            reserved_tokens=0,
            query_tokens=0,
            context_budget=100,
            used_context_tokens=0,
            remaining_tokens=100,
            knowledge_tokens=0,
            memory_tokens=0,
            session_tokens=0,
        )
        assert meta.used_context_tokens == 0
        assert meta.remaining_tokens == 100
