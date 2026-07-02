"""
tests/integration/test_translators.py

Unit tests for Integration Layer Translators.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from integration.translators.knowledge_translator import KnowledgeTranslator
from integration.translators.memory_translator import MemoryTranslator
from integration.translators.session_translator import SessionTranslator
from retriever.knowledge_context import KnowledgeItem
from retriever.memory_context import MemoryEntry
from retriever.session_context import SessionMessage


@dataclass
class FakeDocument:
    text: str
    metadata: dict = field(default_factory=dict)
    score: float = 0.0


class TestKnowledgeTranslator:
    def test_to_domain_full(self) -> None:
        doc = FakeDocument(
            text="Python is a language",
            metadata={"source": "docs/python.md"},
            score=0.95,
        )
        translator = KnowledgeTranslator()
        item = translator.to_domain(doc)

        assert isinstance(item, KnowledgeItem)
        assert item.text == "Python is a language"
        assert item.source == "docs/python.md"
        assert item.score == 0.95

    def test_to_domain_no_source(self) -> None:
        doc = FakeDocument(text="Fact", metadata={}, score=0.0)
        translator = KnowledgeTranslator()
        item = translator.to_domain(doc)

        assert item.source == "Unknown"
        assert item.score is None

    def test_to_domain_zero_score_becomes_none(self) -> None:
        doc = FakeDocument(text="Fact", metadata={"source": "doc"}, score=0.0)
        translator = KnowledgeTranslator()
        item = translator.to_domain(doc)

        assert item.score is None

    def test_to_domain_deterministic(self) -> None:
        doc = FakeDocument(text="Fact", metadata={"source": "doc"}, score=0.5)
        translator = KnowledgeTranslator()
        item1 = translator.to_domain(doc)
        item2 = translator.to_domain(doc)

        assert item1 == item2


class TestMemoryTranslator:
    def test_to_domain_full(self) -> None:
        results = {
            "ids": ["m1", "m2"],
            "documents": ["Likes blue", "Uses Python"],
            "distances": [0.1, 0.2],
        }
        translator = MemoryTranslator()
        entries = translator.to_domain(results)

        assert len(entries) == 2
        assert entries[0].content == "Likes blue"
        assert entries[0].memory_id == "m1"
        assert entries[0].score == 0.1
        assert entries[1].content == "Uses Python"
        assert entries[1].memory_id == "m2"
        assert entries[1].score == 0.2

    def test_to_domain_empty(self) -> None:
        results = {"ids": [], "documents": [], "distances": []}
        translator = MemoryTranslator()
        entries = translator.to_domain(results)

        assert len(entries) == 0

    def test_to_domain_missing_fields(self) -> None:
        results = {"documents": ["Only content"]}
        translator = MemoryTranslator()
        entries = translator.to_domain(results)

        assert len(entries) == 1
        assert entries[0].content == "Only content"
        assert entries[0].memory_id is None
        assert entries[0].score is None

    def test_to_domain_deterministic(self) -> None:
        results = {
            "ids": ["m1"],
            "documents": ["Likes blue"],
            "distances": [0.1],
        }
        translator = MemoryTranslator()
        entries1 = translator.to_domain(results)
        entries2 = translator.to_domain(results)

        assert entries1 == entries2

    def test_to_domain_non_string_content_skipped(self) -> None:
        results = {
            "ids": ["m1"],
            "documents": [123, "Valid"],
            "distances": [0.1, 0.2],
        }
        translator = MemoryTranslator()
        entries = translator.to_domain(results)

        assert len(entries) == 1
        assert entries[0].content == "Valid"


class TestSessionTranslator:
    def test_to_domain_full(self) -> None:
        msg = {"role": "user", "content": "Hello"}
        translator = SessionTranslator()
        result = translator.to_domain(msg)

        assert isinstance(result, SessionMessage)
        assert result.role == "user"
        assert result.content == "Hello"

    def test_to_domain_missing_fields(self) -> None:
        msg = {}
        translator = SessionTranslator()
        result = translator.to_domain(msg)

        assert result.role == ""
        assert result.content == ""

    def test_to_domain_deterministic(self) -> None:
        msg = {"role": "user", "content": "Hello"}
        translator = SessionTranslator()
        result1 = translator.to_domain(msg)
        result2 = translator.to_domain(msg)

        assert result1 == result2
