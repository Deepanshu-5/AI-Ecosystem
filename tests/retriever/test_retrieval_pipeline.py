"""
tests/retriever/test_retrieval_pipeline.py

End-to-end pipeline tests for the Retrieval subsystem.
"""

from __future__ import annotations

import pytest

from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.execution_plan import ExecutionPlan
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements

from retriever.exceptions import InvalidExecutionPlanError
from retriever.knowledge_context import KnowledgeItem
from retriever.knowledge_retriever import KnowledgeRetriever
from retriever.memory_context import MemoryEntry
from retriever.memory_retriever import MemoryRetriever
from retriever.retrieval_builder import RetrievalBuilder
from retriever.retrieved_context import RetrievedContext
from retriever.session_context import SessionMessage
from retriever.session_retriever import SessionRetriever


class TestRetrievalPipeline:
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

    def test_full_pipeline_no_retrieval(self) -> None:
        builder = RetrievalBuilder()
        plan = self._make_plan(knowledge=False, memory=False, session=False)
        ctx = builder.build(plan, "hello world")

        assert isinstance(ctx, RetrievedContext)
        assert ctx.knowledge.items == ()
        assert ctx.memory.entries == ()
        assert ctx.session.recent_messages == ()
        assert ctx.metadata.knowledge_count == 0
        assert ctx.metadata.memory_count == 0
        assert ctx.metadata.session_count == 0
        assert ctx.version == 1

    def test_full_pipeline_knowledge_only(self) -> None:
        def search_knowledge(query: str) -> list[KnowledgeItem]:
            return [
                KnowledgeItem(text="Python is a language", source="docs/python.md"),
                KnowledgeItem(text="FastAPI is a framework", source="docs/fastapi.md"),
            ]

        builder = RetrievalBuilder(
            knowledge_retriever=KnowledgeRetriever(search_fn=search_knowledge),
        )
        plan = self._make_plan(knowledge=True)
        ctx = builder.build(plan, "tell me about python")

        assert isinstance(ctx, RetrievedContext)
        assert len(ctx.knowledge.items) == 2
        assert ctx.knowledge.items[0].text == "Python is a language"
        assert ctx.memory.entries == ()
        assert ctx.session.recent_messages == ()
        assert ctx.metadata.knowledge_count == 2
        assert ctx.metadata.knowledge_latency_ms >= 0

    def test_full_pipeline_memory_only(self) -> None:
        def search_memory(query: str) -> list[MemoryEntry]:
            return [MemoryEntry(content="User prefers dark mode", memory_id="m1")]

        builder = RetrievalBuilder(
            memory_retriever=MemoryRetriever(search_fn=search_memory),
        )
        plan = self._make_plan(memory=True)
        ctx = builder.build(plan, "what do you know about me")

        assert isinstance(ctx, RetrievedContext)
        assert ctx.knowledge.items == ()
        assert len(ctx.memory.entries) == 1
        assert ctx.memory.entries[0].content == "User prefers dark mode"
        assert ctx.session.recent_messages == ()
        assert ctx.metadata.memory_count == 1

    def test_full_pipeline_session_only(self) -> None:
        def get_summary(session_id: str) -> str:
            return "Discussing Python frameworks"

        def get_messages(session_id: str) -> list[SessionMessage]:
            return [
                SessionMessage(role="user", content="What is FastAPI?"),
                SessionMessage(role="assistant", content="A web framework"),
            ]

        builder = RetrievalBuilder(
            session_retriever=SessionRetriever(
                get_summary_fn=get_summary,
                get_messages_fn=get_messages,
            ),
        )
        plan = self._make_plan(session=True)
        ctx = builder.build(plan, "continue", session_id="session_42")

        assert isinstance(ctx, RetrievedContext)
        assert ctx.knowledge.items == ()
        assert ctx.memory.entries == ()
        assert len(ctx.session.recent_messages) == 2
        assert ctx.session.summary == "Discussing Python frameworks"
        assert ctx.metadata.session_count == 2

    def test_full_pipeline_all_resources(self) -> None:
        def search_knowledge(query: str) -> list[KnowledgeItem]:
            return [KnowledgeItem(text="AI systems", source="ai.md")]

        def search_memory(query: str) -> list[MemoryEntry]:
            return [MemoryEntry(content="Likes AI", memory_id="m1")]

        def get_summary(session_id: str) -> str:
            return "AI discussion"

        def get_messages(session_id: str) -> list[SessionMessage]:
            return [SessionMessage(role="user", content="Hello")]

        builder = RetrievalBuilder(
            knowledge_retriever=KnowledgeRetriever(search_fn=search_knowledge),
            memory_retriever=MemoryRetriever(search_fn=search_memory),
            session_retriever=SessionRetriever(
                get_summary_fn=get_summary,
                get_messages_fn=get_messages,
            ),
        )
        plan = self._make_plan(knowledge=True, memory=True, session=True)
        ctx = builder.build(plan, "what about ai", session_id="s1")

        assert isinstance(ctx, RetrievedContext)
        assert len(ctx.knowledge.items) == 1
        assert len(ctx.memory.entries) == 1
        assert len(ctx.session.recent_messages) == 1
        assert ctx.metadata.knowledge_count == 1
        assert ctx.metadata.memory_count == 1
        assert ctx.metadata.session_count == 1
        assert ctx.metadata.total_latency_ms >= 0

    def test_pipeline_replayable(self) -> None:
        def search_knowledge(query: str) -> list[KnowledgeItem]:
            return [KnowledgeItem(text="Fact", source="doc")]

        builder = RetrievalBuilder(
            knowledge_retriever=KnowledgeRetriever(search_fn=search_knowledge),
        )
        plan = self._make_plan(knowledge=True)

        ctx1 = builder.build(plan, "query")
        ctx2 = builder.build(plan, "query")

        assert ctx1.knowledge == ctx2.knowledge
        assert ctx1.memory == ctx2.memory
        assert ctx1.session == ctx2.session
        assert ctx1.metadata.knowledge_count == ctx2.metadata.knowledge_count

    def test_pipeline_empty_results_valid(self) -> None:
        def search_knowledge(query: str) -> list[KnowledgeItem]:
            return []

        def search_memory(query: str) -> list[MemoryEntry]:
            return []

        def get_summary(session_id: str) -> str:
            return ""

        def get_messages(session_id: str) -> list[SessionMessage]:
            return []

        builder = RetrievalBuilder(
            knowledge_retriever=KnowledgeRetriever(search_fn=search_knowledge),
            memory_retriever=MemoryRetriever(search_fn=search_memory),
            session_retriever=SessionRetriever(
                get_summary_fn=get_summary,
                get_messages_fn=get_messages,
            ),
        )
        plan = self._make_plan(knowledge=True, memory=True, session=True)
        ctx = builder.build(plan, "query", session_id="s1")

        assert ctx.knowledge.items == ()
        assert ctx.memory.entries == ()
        assert ctx.session.recent_messages == ()
        assert ctx.metadata.knowledge_count == 0
        assert ctx.metadata.memory_count == 0
        assert ctx.metadata.session_count == 0

    def test_pipeline_fail_fast_on_bad_plan(self) -> None:
        builder = RetrievalBuilder()
        with pytest.raises(InvalidExecutionPlanError):
            builder.build(None, "query")  # type: ignore[arg-type]

    def test_pipeline_fail_fast_on_bad_query(self) -> None:
        builder = RetrievalBuilder()
        plan = self._make_plan()
        with pytest.raises(InvalidExecutionPlanError):
            builder.build(plan, "")

    def test_serialization_roundtrip(self) -> None:
        def search_knowledge(query: str) -> list[KnowledgeItem]:
            return [KnowledgeItem(text="Fact", source="doc")]

        builder = RetrievalBuilder(
            knowledge_retriever=KnowledgeRetriever(search_fn=search_knowledge),
        )
        plan = self._make_plan(knowledge=True)
        ctx = builder.build(plan, "query")

        d = ctx.to_dict()
        assert isinstance(d, dict)
        assert "knowledge" in d
        assert "memory" in d
        assert "session" in d
        assert "metadata" in d
        assert "version" in d
        assert d["version"] == 1
