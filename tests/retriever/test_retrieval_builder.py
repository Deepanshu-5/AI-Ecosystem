"""
tests/retriever/test_retrieval_builder.py

Builder tests for RetrievalBuilder.
"""

from __future__ import annotations

import pytest

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.execution_plan import ExecutionPlan
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements

from retriever.exceptions import InvalidExecutionPlanError
from retriever.knowledge_context import KnowledgeContext, KnowledgeItem
from retriever.knowledge_retriever import KnowledgeRetriever
from retriever.memory_context import MemoryContext, MemoryEntry
from retriever.memory_retriever import MemoryRetriever
from retriever.retrieval_builder import RetrievalBuilder
from retriever.session_context import SessionContext, SessionMessage
from retriever.session_retriever import SessionRetriever


class TestRetrievalBuilder:
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

    def _make_knowledge_retriever(self) -> KnowledgeRetriever:
        def search_fn(query: str) -> list[KnowledgeItem]:
            return [KnowledgeItem(text="Fact", source="doc")]
        return KnowledgeRetriever(search_fn=search_fn)

    def _make_memory_retriever(self) -> MemoryRetriever:
        def search_fn(query: str) -> list[MemoryEntry]:
            return [MemoryEntry(content="Pref")]
        return MemoryRetriever(search_fn=search_fn)

    def _make_session_retriever(self) -> SessionRetriever:
        def get_summary(session_id: str) -> str:
            return "Summary"
        def get_messages(session_id: str) -> list[SessionMessage]:
            return [SessionMessage(role="user", content="Hi")]
        return SessionRetriever(
            get_summary_fn=get_summary,
            get_messages_fn=get_messages,
        )

    def test_build_no_resources(self) -> None:
        builder = RetrievalBuilder()
        plan = self._make_plan(knowledge=False, memory=False, session=False)
        ctx = builder.build(plan, "query")

        assert ctx.knowledge.items == ()
        assert ctx.memory.entries == ()
        assert ctx.session.recent_messages == ()
        assert ctx.metadata.knowledge_count == 0
        assert ctx.metadata.memory_count == 0
        assert ctx.metadata.session_count == 0

    def test_build_with_knowledge_only(self) -> None:
        builder = RetrievalBuilder(
            knowledge_retriever=self._make_knowledge_retriever(),
        )
        plan = self._make_plan(knowledge=True, memory=False, session=False)
        ctx = builder.build(plan, "query")

        assert len(ctx.knowledge.items) == 1
        assert ctx.knowledge.items[0].text == "Fact"
        assert ctx.memory.entries == ()
        assert ctx.session.recent_messages == ()
        assert ctx.metadata.knowledge_count == 1

    def test_build_with_memory_only(self) -> None:
        builder = RetrievalBuilder(
            memory_retriever=self._make_memory_retriever(),
        )
        plan = self._make_plan(knowledge=False, memory=True, session=False)
        ctx = builder.build(plan, "query")

        assert ctx.knowledge.items == ()
        assert len(ctx.memory.entries) == 1
        assert ctx.session.recent_messages == ()
        assert ctx.metadata.memory_count == 1

    def test_build_with_session_only(self) -> None:
        builder = RetrievalBuilder(
            session_retriever=self._make_session_retriever(),
        )
        plan = self._make_plan(knowledge=False, memory=False, session=True)
        ctx = builder.build(plan, "query", session_id="s1")

        assert ctx.knowledge.items == ()
        assert ctx.memory.entries == ()
        assert len(ctx.session.recent_messages) == 1
        assert ctx.session.summary == "Summary"
        assert ctx.metadata.session_count == 1

    def test_build_with_all_resources(self) -> None:
        builder = RetrievalBuilder(
            knowledge_retriever=self._make_knowledge_retriever(),
            memory_retriever=self._make_memory_retriever(),
            session_retriever=self._make_session_retriever(),
        )
        plan = self._make_plan(knowledge=True, memory=True, session=True)
        ctx = builder.build(plan, "query", session_id="s1")

        assert len(ctx.knowledge.items) == 1
        assert len(ctx.memory.entries) == 1
        assert len(ctx.session.recent_messages) == 1

    def test_build_missing_knowledge_retriever(self) -> None:
        builder = RetrievalBuilder()
        plan = self._make_plan(knowledge=True)
        with pytest.raises(InvalidExecutionPlanError):
            builder.build(plan, "query")

    def test_build_missing_memory_retriever(self) -> None:
        builder = RetrievalBuilder()
        plan = self._make_plan(memory=True)
        with pytest.raises(InvalidExecutionPlanError):
            builder.build(plan, "query")

    def test_build_missing_session_retriever(self) -> None:
        builder = RetrievalBuilder()
        plan = self._make_plan(session=True)
        with pytest.raises(InvalidExecutionPlanError):
            builder.build(plan, "query", session_id="s1")

    def test_build_missing_session_id(self) -> None:
        builder = RetrievalBuilder(
            session_retriever=self._make_session_retriever(),
        )
        plan = self._make_plan(session=True)
        with pytest.raises(InvalidExecutionPlanError):
            builder.build(plan, "query")

    def test_build_none_execution_plan(self) -> None:
        builder = RetrievalBuilder()
        with pytest.raises(InvalidExecutionPlanError):
            builder.build(None, "query")  # type: ignore[arg-type]

    def test_build_empty_query(self) -> None:
        builder = RetrievalBuilder()
        plan = self._make_plan()
        with pytest.raises(InvalidExecutionPlanError):
            builder.build(plan, "")

    def test_build_whitespace_query(self) -> None:
        builder = RetrievalBuilder()
        plan = self._make_plan()
        with pytest.raises(InvalidExecutionPlanError):
            builder.build(plan, "   ")

    def test_latency_is_non_negative(self) -> None:
        builder = RetrievalBuilder(
            knowledge_retriever=self._make_knowledge_retriever(),
        )
        plan = self._make_plan(knowledge=True)
        ctx = builder.build(plan, "query")

        assert ctx.metadata.knowledge_latency_ms >= 0
        assert ctx.metadata.total_latency_ms >= 0

    def test_deterministic_same_input(self) -> None:
        builder = RetrievalBuilder(
            knowledge_retriever=self._make_knowledge_retriever(),
        )
        plan = self._make_plan(knowledge=True)
        ctx1 = builder.build(plan, "query")
        ctx2 = builder.build(plan, "query")

        assert ctx1.knowledge == ctx2.knowledge
        assert ctx1.memory == ctx2.memory
        assert ctx1.session == ctx2.session

    def test_empty_retrieval_is_valid(self) -> None:
        def empty_search(query: str) -> list[KnowledgeItem]:
            return []
        builder = RetrievalBuilder(
            knowledge_retriever=KnowledgeRetriever(search_fn=empty_search),
        )
        plan = self._make_plan(knowledge=True)
        ctx = builder.build(plan, "query")

        assert ctx.knowledge.items == ()
        assert ctx.metadata.knowledge_count == 0
