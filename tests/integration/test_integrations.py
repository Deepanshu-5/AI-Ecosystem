"""
tests/integration/test_integrations.py

Unit tests for individual Integration components
(KnowledgeIntegration, MemoryIntegration, SessionIntegration).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from integration.exceptions import KnowledgeIntegrationError
from integration.gateways.knowledge_gateway import KnowledgeGateway
from integration.gateways.memory_gateway import MemoryGateway
from integration.gateways.session_gateway import SessionGateway
from integration.integrations.knowledge_integration import KnowledgeIntegration
from integration.integrations.memory_integration import MemoryIntegration
from integration.integrations.session_integration import SessionIntegration
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


class TestKnowledgeIntegration:
    def test_search_returns_domain_objects(self) -> None:
        def fake_search(query: str, top_k: int, final_k: int) -> list[FakeDocument]:
            return [
                FakeDocument(text="Fact A", metadata={"source": "doc1"}, score=0.95),
                FakeDocument(text="Fact B", metadata={"source": "doc2"}, score=0.88),
            ]

        gateway = KnowledgeGateway(search_fn=fake_search)
        integration = KnowledgeIntegration(gateway=gateway, translator=KnowledgeTranslator())
        items = integration.search("query", top_k=5, final_k=3)

        assert len(items) == 2
        assert isinstance(items[0], KnowledgeItem)
        assert items[0].text == "Fact A"
        assert items[0].source == "doc1"
        assert items[1].text == "Fact B"

    def test_search_empty_results(self) -> None:
        def fake_search(query: str, top_k: int, final_k: int) -> list:
            return []

        gateway = KnowledgeGateway(search_fn=fake_search)
        integration = KnowledgeIntegration(gateway=gateway, translator=KnowledgeTranslator())
        items = integration.search("query")

        assert len(items) == 0

    def test_search_propagates_gateway_error(self) -> None:
        def fake_search(query: str, top_k: int, final_k: int) -> list:
            raise RuntimeError("infra down")

        gateway = KnowledgeGateway(search_fn=fake_search)
        integration = KnowledgeIntegration(gateway=gateway, translator=KnowledgeTranslator())
        with pytest.raises(KnowledgeIntegrationError):
            integration.search("query")

    def test_default_construction(self) -> None:
        integration = KnowledgeIntegration()
        assert integration._gateway is not None
        assert integration._translator is not None

    def test_search_deterministic(self) -> None:
        def fake_search(query: str, top_k: int, final_k: int) -> list[FakeDocument]:
            return [FakeDocument(text="Fact", metadata={"source": "doc"}, score=0.5)]

        gateway = KnowledgeGateway(search_fn=fake_search)
        integration = KnowledgeIntegration(gateway=gateway, translator=KnowledgeTranslator())
        items1 = integration.search("same")
        items2 = integration.search("same")
        assert items1 == items2


class TestMemoryIntegration:
    def test_search_returns_domain_objects(self) -> None:
        def fake_search(query: str, top_k: int) -> dict[str, list]:
            return {
                "ids": ["m1", "m2"],
                "documents": ["Likes blue", "Uses Python"],
                "distances": [0.1, 0.2],
            }

        gateway = MemoryGateway(search_fn=fake_search)
        integration = MemoryIntegration(gateway=gateway, translator=MemoryTranslator())
        entries = integration.search("query", top_k=3)

        assert len(entries) == 2
        assert isinstance(entries[0], MemoryEntry)
        assert entries[0].content == "Likes blue"
        assert entries[0].memory_id == "m1"
        assert entries[0].score == 0.9

    def test_search_empty_results(self) -> None:
        def fake_search(query: str, top_k: int) -> dict[str, list]:
            return {"ids": [], "documents": [], "distances": []}

        gateway = MemoryGateway(search_fn=fake_search)
        integration = MemoryIntegration(gateway=gateway, translator=MemoryTranslator())
        entries = integration.search("query")

        assert len(entries) == 0

    def test_default_construction(self) -> None:
        integration = MemoryIntegration()
        assert integration._gateway is not None
        assert integration._translator is not None

    def test_search_deterministic(self) -> None:
        def fake_search(query: str, top_k: int) -> dict[str, list]:
            return {"ids": ["m1"], "documents": ["Likes blue"], "distances": [0.1]}

        gateway = MemoryGateway(search_fn=fake_search)
        integration = MemoryIntegration(gateway=gateway, translator=MemoryTranslator())
        entries1 = integration.search("same")
        entries2 = integration.search("same")
        assert entries1 == entries2


class TestSessionIntegration:
    def test_get_summary(self) -> None:
        def fake_load(session_id: str) -> str:
            return "Summary"

        def fake_messages(session_id: str) -> list[dict[str, str]]:
            return []

        gateway = SessionGateway(
            load_summary_fn=fake_load,
            get_messages_fn=fake_messages,
        )
        integration = SessionIntegration(gateway=gateway, translator=SessionTranslator())
        summary = integration.get_summary("s1")

        assert summary == "Summary"

    def test_get_messages(self) -> None:
        def fake_load(session_id: str) -> str:
            return ""

        def fake_messages(session_id: str) -> list[dict[str, str]]:
            return [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"},
            ]

        gateway = SessionGateway(
            load_summary_fn=fake_load,
            get_messages_fn=fake_messages,
        )
        integration = SessionIntegration(gateway=gateway, translator=SessionTranslator())
        messages = integration.get_messages("s1")

        assert len(messages) == 2
        assert isinstance(messages[0], SessionMessage)
        assert messages[0].role == "user"
        assert messages[0].content == "Hello"
        assert messages[1].role == "assistant"
        assert messages[1].content == "Hi there"

    def test_get_messages_empty(self) -> None:
        def fake_load(session_id: str) -> str:
            return ""

        def fake_messages(session_id: str) -> list[dict[str, str]]:
            return []

        gateway = SessionGateway(
            load_summary_fn=fake_load,
            get_messages_fn=fake_messages,
        )
        integration = SessionIntegration(gateway=gateway, translator=SessionTranslator())
        messages = integration.get_messages("s1")

        assert len(messages) == 0

    def test_default_construction(self) -> None:
        integration = SessionIntegration()
        assert integration._gateway is not None
        assert integration._translator is not None

    def test_deterministic(self) -> None:
        def fake_load(session_id: str) -> str:
            return "Summary"

        def fake_messages(session_id: str) -> list[dict[str, str]]:
            return [{"role": "user", "content": "Hello"}]

        gateway = SessionGateway(
            load_summary_fn=fake_load,
            get_messages_fn=fake_messages,
        )
        integration = SessionIntegration(gateway=gateway, translator=SessionTranslator())
        summary1 = integration.get_summary("s1")
        summary2 = integration.get_summary("s1")
        messages1 = integration.get_messages("s1")
        messages2 = integration.get_messages("s1")

        assert summary1 == summary2
        assert messages1 == messages2
