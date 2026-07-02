"""
tests/integration/test_gateways.py

Unit tests for Integration Layer Gateways.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from integration.exceptions import KnowledgeIntegrationError, MemoryIntegrationError, SessionIntegrationError
from integration.gateways.knowledge_gateway import KnowledgeGateway
from integration.gateways.memory_gateway import MemoryGateway
from integration.gateways.session_gateway import SessionGateway


@dataclass
class FakeDocument:
    text: str
    metadata: dict = field(default_factory=dict)
    score: float = 0.0


class TestKnowledgeGateway:
    def test_search_delegates_to_infrastructure(self) -> None:
        called = {"args": None}

        def fake_search(query: str, top_k: int, final_k: int) -> list[FakeDocument]:
            called["args"] = (query, top_k, final_k)
            return [FakeDocument(text="fact", metadata={"source": "doc"})]

        gateway = KnowledgeGateway(search_fn=fake_search)
        result = gateway.search("test", top_k=5, final_k=3)

        assert called["args"] == ("test", 5, 3)
        assert len(result) == 1
        assert result[0].text == "fact"

    def test_search_wraps_exception(self) -> None:
        def failing_search(query: str, top_k: int, final_k: int) -> list:
            raise RuntimeError("db down")

        gateway = KnowledgeGateway(search_fn=failing_search)
        with pytest.raises(KnowledgeIntegrationError) as exc_info:
            gateway.search("test")
        assert isinstance(exc_info.value.__cause__, RuntimeError)
        assert "db down" in str(exc_info.value.__cause__)

    def test_search_default_function(self) -> None:
        # Verify the gateway can be constructed with defaults
        gateway = KnowledgeGateway()
        assert gateway._search_fn is not None


class TestMemoryGateway:
    def test_search_delegates_to_infrastructure(self) -> None:
        called = {"args": None}

        def fake_search(query: str, top_k: int) -> dict[str, list]:
            called["args"] = (query, top_k)
            return {"ids": ["m1"], "documents": ["memory"], "distances": [0.1]}

        gateway = MemoryGateway(search_fn=fake_search)
        result = gateway.search("test", top_k=3)

        assert called["args"] == ("test", 3)
        assert result["ids"] == ["m1"]

    def test_search_wraps_exception(self) -> None:
        def failing_search(query: str, top_k: int) -> dict:
            raise RuntimeError("memory down")

        gateway = MemoryGateway(search_fn=failing_search)
        with pytest.raises(MemoryIntegrationError) as exc_info:
            gateway.search("test")
        assert isinstance(exc_info.value.__cause__, RuntimeError)
        assert "memory down" in str(exc_info.value.__cause__)

    def test_search_default_function(self) -> None:
        gateway = MemoryGateway()
        assert gateway._search_fn is not None


class TestSessionGateway:
    def test_load_summary_delegates(self) -> None:
        called = {"args": None}

        def fake_load(session_id: str) -> str:
            called["args"] = session_id
            return "Summary text"

        def fake_messages(session_id: str) -> list[dict[str, str]]:
            return []

        gateway = SessionGateway(
            load_summary_fn=fake_load,
            get_messages_fn=fake_messages,
        )
        result = gateway.load_summary("s1")

        assert called["args"] == "s1"
        assert result == "Summary text"

    def test_get_messages_delegates(self) -> None:
        called = {"args": None}

        def fake_load(session_id: str) -> str:
            return ""

        def fake_messages(session_id: str) -> list[dict[str, str]]:
            called["args"] = session_id
            return [{"role": "user", "content": "Hello"}]

        gateway = SessionGateway(
            load_summary_fn=fake_load,
            get_messages_fn=fake_messages,
        )
        result = gateway.get_recent_messages("s1")

        assert called["args"] == "s1"
        assert len(result) == 1
        assert result[0]["role"] == "user"

    def test_load_summary_wraps_exception(self) -> None:
        def failing_load(session_id: str) -> str:
            raise RuntimeError("store down")

        gateway = SessionGateway(
            load_summary_fn=failing_load,
            get_messages_fn=lambda sid: [],
        )
        with pytest.raises(SessionIntegrationError) as exc_info:
            gateway.load_summary("s1")
        assert isinstance(exc_info.value.__cause__, RuntimeError)
        assert "store down" in str(exc_info.value.__cause__)

    def test_get_messages_wraps_exception(self) -> None:
        def failing_messages(session_id: str) -> list[dict[str, str]]:
            raise RuntimeError("manager down")

        gateway = SessionGateway(
            load_summary_fn=lambda sid: "",
            get_messages_fn=failing_messages,
        )
        with pytest.raises(SessionIntegrationError) as exc_info:
            gateway.get_recent_messages("s1")
        assert isinstance(exc_info.value.__cause__, RuntimeError)
        assert "manager down" in str(exc_info.value.__cause__)

    def test_default_functions(self) -> None:
        gateway = SessionGateway()
        assert gateway._load_summary_fn is not None
        assert gateway._get_messages_fn is not None
