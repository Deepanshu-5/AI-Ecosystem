"""
tests/integration/test_retriever_integration.py

End-to-end tests for RetrieverIntegration.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.execution_plan import ExecutionPlan
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements

from integration.exceptions import KnowledgeIntegrationError
from integration.gateways.knowledge_gateway import KnowledgeGateway
from integration.gateways.memory_gateway import MemoryGateway
from integration.gateways.session_gateway import SessionGateway
from integration.integrations.knowledge_integration import KnowledgeIntegration
from integration.integrations.memory_integration import MemoryIntegration
from integration.integrations.retriever_integration import RetrieverIntegration
from integration.integrations.session_integration import SessionIntegration
from integration.translators.knowledge_translator import KnowledgeTranslator
from integration.translators.memory_translator import MemoryTranslator
from integration.translators.session_translator import SessionTranslator
from retriever.exceptions import InvalidExecutionPlanError
from retriever.retrieved_context import RetrievedContext


@dataclass
class FakeDocument:
    text: str
    metadata: dict = field(default_factory=dict)
    score: float = 0.0


class TestRetrieverIntegration:
    def _make_plan(
        self,
        knowledge: bool = False,
        memory: bool = False,
        session: bool = False,
    ) -> ExecutionPlan:
        return ExecutionPlan(
            processing_goal=ProcessingGoal.GENERAL,
            complexity=Complexity.LOW,
            resource_requirements=ResourceRequirements(
                knowledge=knowledge,
                memory=memory,
                session=session,
            ),
            decision_trace=DecisionTrace(
                processing_goal_reason="test",
                complexity_reason="test",
                resource_requirements_reason="test",
            ),
        )

    def _make_knowledge_integration(self) -> KnowledgeIntegration:
        def fake_search(query: str, top_k: int, final_k: int) -> list[FakeDocument]:
            return [
                FakeDocument(text="Python fact", metadata={"source": "docs/python.md"}, score=0.95),
            ]

        gateway = KnowledgeGateway(search_fn=fake_search)
        return KnowledgeIntegration(gateway=gateway, translator=KnowledgeTranslator())

    def _make_memory_integration(self) -> MemoryIntegration:
        def fake_search(query: str, top_k: int) -> dict[str, list]:
            return {
                "ids": ["m1"],
                "documents": ["Likes blue"],
                "distances": [0.1],
            }

        gateway = MemoryGateway(search_fn=fake_search)
        return MemoryIntegration(gateway=gateway, translator=MemoryTranslator())

    def _make_session_integration(self) -> SessionIntegration:
        def fake_load(session_id: str) -> str:
            return "Summary"

        def fake_messages(session_id: str) -> list[dict[str, str]]:
            return [{"role": "user", "content": "Hello"}]

        gateway = SessionGateway(
            load_summary_fn=fake_load,
            get_messages_fn=fake_messages,
        )
        return SessionIntegration(gateway=gateway, translator=SessionTranslator())

    def test_no_resources(self) -> None:
        ri = RetrieverIntegration()
        plan = self._make_plan(knowledge=False, memory=False, session=False)
        ctx = ri.build(plan, "hello")

        assert isinstance(ctx, RetrievedContext)
        assert ctx.knowledge.items == ()
        assert ctx.memory.entries == ()
        assert ctx.session.recent_messages == ()
        assert ctx.metadata.knowledge_count == 0
        assert ctx.metadata.memory_count == 0
        assert ctx.metadata.session_count == 0

    def test_knowledge_only(self) -> None:
        ri = RetrieverIntegration(knowledge_integration=self._make_knowledge_integration())
        plan = self._make_plan(knowledge=True)
        ctx = ri.build(plan, "python")

        assert isinstance(ctx, RetrievedContext)
        assert len(ctx.knowledge.items) == 1
        assert ctx.knowledge.items[0].text == "Python fact"
        assert ctx.memory.entries == ()
        assert ctx.session.recent_messages == ()

    def test_memory_only(self) -> None:
        ri = RetrieverIntegration(memory_integration=self._make_memory_integration())
        plan = self._make_plan(memory=True)
        ctx = ri.build(plan, "preferences")

        assert isinstance(ctx, RetrievedContext)
        assert ctx.knowledge.items == ()
        assert len(ctx.memory.entries) == 1
        assert ctx.memory.entries[0].content == "Likes blue"
        assert ctx.session.recent_messages == ()

    def test_session_only(self) -> None:
        ri = RetrieverIntegration(session_integration=self._make_session_integration())
        plan = self._make_plan(session=True)
        ctx = ri.build(plan, "continue", session_id="s1")

        assert isinstance(ctx, RetrievedContext)
        assert ctx.knowledge.items == ()
        assert ctx.memory.entries == ()
        assert len(ctx.session.recent_messages) == 1
        assert ctx.session.summary == "Summary"
        assert ctx.session.recent_messages[0].role == "user"

    def test_all_resources(self) -> None:
        ri = RetrieverIntegration(
            knowledge_integration=self._make_knowledge_integration(),
            memory_integration=self._make_memory_integration(),
            session_integration=self._make_session_integration(),
        )
        plan = self._make_plan(knowledge=True, memory=True, session=True)
        ctx = ri.build(plan, "python", session_id="s1")

        assert isinstance(ctx, RetrievedContext)
        assert len(ctx.knowledge.items) == 1
        assert len(ctx.memory.entries) == 1
        assert len(ctx.session.recent_messages) == 1

    def test_deterministic(self) -> None:
        ri = RetrieverIntegration(knowledge_integration=self._make_knowledge_integration())
        plan = self._make_plan(knowledge=True)
        ctx1 = ri.build(plan, "python")
        ctx2 = ri.build(plan, "python")

        assert ctx1.knowledge == ctx2.knowledge
        assert ctx1.memory == ctx2.memory
        assert ctx1.session == ctx2.session

    def test_empty_retrieval_valid(self) -> None:
        def fake_search(query: str, top_k: int, final_k: int) -> list:
            return []

        gateway = KnowledgeGateway(search_fn=fake_search)
        ki = KnowledgeIntegration(gateway=gateway, translator=KnowledgeTranslator())
        ri = RetrieverIntegration(knowledge_integration=ki)
        plan = self._make_plan(knowledge=True)
        ctx = ri.build(plan, "query")

        assert ctx.knowledge.items == ()
        assert ctx.metadata.knowledge_count == 0

    def test_invalid_execution_plan(self) -> None:
        ri = RetrieverIntegration()
        with pytest.raises(InvalidExecutionPlanError):
            ri.build(None, "query")  # type: ignore[arg-type]

    def test_infrastructure_failure_translated(self) -> None:
        def fake_search(query: str, top_k: int, final_k: int) -> list:
            raise RuntimeError("db down")

        gateway = KnowledgeGateway(search_fn=fake_search)
        ki = KnowledgeIntegration(gateway=gateway, translator=KnowledgeTranslator())
        ri = RetrieverIntegration(knowledge_integration=ki)
        plan = self._make_plan(knowledge=True)
        with pytest.raises(KnowledgeIntegrationError):
            ri.build(plan, "query")

    def test_serialization_roundtrip(self) -> None:
        ri = RetrieverIntegration(knowledge_integration=self._make_knowledge_integration())
        plan = self._make_plan(knowledge=True)
        ctx = ri.build(plan, "python")

        d = ctx.to_dict()
        assert isinstance(d, dict)
        assert "knowledge" in d
        assert "memory" in d
        assert "session" in d
        assert "metadata" in d
        assert "version" in d

    def test_public_api_import(self) -> None:
        from integration import RetrieverIntegration
        assert RetrieverIntegration is not None
