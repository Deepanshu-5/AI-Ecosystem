"""
integration/integrations/retriever_integration.py

Coordinates the complete retrieval integration workflow.
"""

from __future__ import annotations

from planner.execution_plan import ExecutionPlan

from integration.integrations.knowledge_integration import KnowledgeIntegration
from integration.integrations.memory_integration import MemoryIntegration
from integration.integrations.session_integration import SessionIntegration
from retriever.knowledge_retriever import KnowledgeRetriever
from retriever.memory_retriever import MemoryRetriever
from retriever.retrieval_builder import RetrievalBuilder
from retriever.retrieved_context import RetrievedContext
from retriever.session_retriever import SessionRetriever


class RetrieverIntegration:
    """
    Coordinates the complete retrieval integration workflow.

    Purpose:
        Bridges the Retriever Domain Layer with the existing
        Infrastructure Layer. Receives a retrieval request from the
        Control Plane, creates the individual retrievers wired to
        the Integration Layer, invokes the RetrievalBuilder, and
        returns the immutable RetrievedContext.

    Owned by:
        integration/integrations/retriever_integration.py

    Consumed by:
        Control Plane, downstream orchestration layer.

    Invariants:
        - Never performs business logic.
        - Never communicates directly with infrastructure.
        - Never translates objects.
        - Never modifies RetrievedContext.
        - Owns orchestration only.
    """

    def __init__(
        self,
        knowledge_integration: KnowledgeIntegration | None = None,
        memory_integration: MemoryIntegration | None = None,
        session_integration: SessionIntegration | None = None,
    ) -> None:
        """
        Initialise RetrieverIntegration.

        Parameters:
            knowledge_integration (KnowledgeIntegration | None):
                Knowledge integration component. If None, a default
                KnowledgeIntegration is constructed.
            memory_integration (MemoryIntegration | None):
                Memory integration component. If None, a default
                MemoryIntegration is constructed.
            session_integration (SessionIntegration | None):
                Session integration component. If None, a default
                SessionIntegration is constructed.

        Returns:
            None.

        Raises:
            None.

        Side Effects:
            None.
        """
        self._knowledge_integration = (
            knowledge_integration if knowledge_integration is not None else KnowledgeIntegration()
        )
        self._memory_integration = (
            memory_integration if memory_integration is not None else MemoryIntegration()
        )
        self._session_integration = (
            session_integration if session_integration is not None else SessionIntegration()
        )

    def build(
        self,
        execution_plan: ExecutionPlan,
        query: str,
        session_id: str | None = None,
    ) -> RetrievedContext:
        """
        Execute the complete retrieval integration pipeline.

        The pipeline follows the deterministic architecture:
        1. Create individual retrievers wired to Integration Layer.
        2. Invoke RetrievalBuilder with the ExecutionPlan.
        3. Return the validated, immutable RetrievedContext.

        Parameters:
            execution_plan (ExecutionPlan): The immutable plan
                produced by the Planner. Determines which retrievers
                are invoked.
            query (str): The original user query. Required for
                knowledge and memory retrieval.
            session_id (str | None): The active session identifier.
                Required when session retrieval is requested.

        Returns:
            RetrievedContext: A validated, immutable context
            containing all retrieved information and metadata.

        Raises:
            InvalidExecutionPlanError: Propagated from the
                RetrievalBuilder if the ExecutionPlan is invalid.
            RetrieverError: Propagated from the RetrievalBuilder if
                any retrieval fails.

        Side Effects:
            None. The Integration Layer may trigger infrastructure
            access, but RetrieverIntegration itself performs no side
            effects.
        """
        builder = RetrievalBuilder(
            knowledge_retriever=KnowledgeRetriever(
                search_fn=self._knowledge_integration.search
            ),
            memory_retriever=MemoryRetriever(
                search_fn=self._memory_integration.search
            ),
            session_retriever=SessionRetriever(
                get_summary_fn=self._session_integration.get_summary,
                get_messages_fn=self._session_integration.get_messages,
            ),
        )
        return builder.build(execution_plan, query, session_id)
