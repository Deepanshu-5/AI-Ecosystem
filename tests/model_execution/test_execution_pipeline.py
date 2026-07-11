from budgeting.budget_metadata import BudgetMetadata
from budgeting.budgeted_context import BudgetedContext
from llm.base_generator import BaseGenerator
from model_execution.model_execution_integration import ModelExecutionIntegration
from planner.complexity import Complexity
from planner.decision_trace import DecisionTrace
from planner.execution_plan import ExecutionPlan
from planner.processing_goal import ProcessingGoal
from planner.resource_requirements import ResourceRequirements
from prompt_builder.prompt_builder import PromptBuilder
from retriever.knowledge_context import KnowledgeContext
from retriever.memory_context import MemoryContext
from retriever.session_context import SessionContext
from routing.model_router import ModelRouter


class _Generator(BaseGenerator):
    def __init__(self) -> None:
        self.received: list[str] = []

    def generate(self, prompt: str) -> str:
        self.received.append(prompt)
        return "pipeline response"


def _budgeted_context() -> BudgetedContext:
    return BudgetedContext(
        knowledge=KnowledgeContext(items=(), metadata={}),
        memory=MemoryContext(entries=(), metadata={}),
        session=SessionContext(summary="", recent_messages=(), metadata={}),
        metadata=BudgetMetadata(100, 20, 5, 75, 0, 75, 0, 0, 0),
        effective_query="hello",
    )


def _execution_plan() -> ExecutionPlan:
    return ExecutionPlan(
        processing_goal=ProcessingGoal.GENERAL,
        complexity=Complexity.LOW,
        resource_requirements=ResourceRequirements(False, False, False),
        decision_trace=DecisionTrace("general", "low", "none"),
    )


def test_prompt_builder_and_model_router_outputs_reach_execution_unchanged() -> None:
    prompt = PromptBuilder(token_counter=len).build(_budgeted_context())
    route = ModelRouter.route(_execution_plan())
    generator = _Generator()

    response = ModelExecutionIntegration().execute(prompt, route, generator)

    assert generator.received == [prompt.content]
    assert response.content == "pipeline response"
    assert prompt == PromptBuilder(token_counter=len).build(_budgeted_context())
    assert route == ModelRouter.route(_execution_plan())
