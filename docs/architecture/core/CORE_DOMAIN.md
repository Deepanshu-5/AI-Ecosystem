Version: 1.0

Status: Production Ready

Architecture Status: Frozen

Production Target: Production V1

Current Phase: Production V1 Freeze

Review Requirement:
Architecture Review Required Before Modification

4. Core Domain

The Core Domain defines the conceptual model of the AI Ecosystem.

It is independent of programming languages, frameworks, databases, language models, or infrastructure.

The purpose of the Core Domain is to provide a stable vocabulary and set of contracts that describe how the system reasons.

Infrastructure may change.

Implementations may change.

The Core Domain should remain stable.

---

4.1 Core Domain Philosophy

The AI Ecosystem is fundamentally a decision-making system.

Its responsibility is not to execute work.

Its responsibility is to determine how work should be executed.

The Core Domain therefore models decisions rather than implementations.

Every domain object should represent a stable concept rather than a technical implementation.

---

4.2 Ubiquitous Language

The following terminology has a single meaning throughout the project.

The same word must never represent different concepts.

Query

The original user request entering the AI Ecosystem.

---

Planner

The architectural component responsible for analyzing a query and producing an ExecutionPlan.

The Planner never performs retrieval or execution.

---

ExecutionPlan

The immutable domain contract produced by the Planner.

It represents every planning decision required by downstream components.

ExecutionPlan is consumed by the rest of the ecosystem.

ExecutionPlan never executes work.

---

ProcessingGoal

The Planner's classification of the primary processing domain required to satisfy the query.

Examples include:

- General
- Knowledge
- Memory
- Session
- Document
- Code

ProcessingGoal describes what kind of problem is being solved.

It does not describe implementation.

---

ResourceRequirement

Represents which ecosystem resources are required.

Examples include:

- Knowledge
- Memory
- Session

Resource requirements describe required resources rather than execution behaviour.

---

DecisionTrace

A structured explanation describing why the Planner reached its decisions.

DecisionTrace exists only for explainability.

It never changes planner decisions.

---

Context

Information selected for potential inclusion in the final prompt.

Context is divided into:

- Knowledge Context
- Memory Context
- Session Context

Context exists before budgeting.

---

BudgetedContext

Context remaining after Context Budgeting.

BudgetedContext is the only context passed to Prompt Construction.

---

Prompt

The final structured input delivered to a language model.

Prompt construction occurs after planning and budgeting.

---

Retriever

The architectural component responsible for locating and returning the knowledge, memory, and session information required by the ExecutionPlan. The Retriever never constructs prompts or executes models or tools.

---

Context Budgeting

The subsystem responsible for allocating, prioritizing, and trimming context before prompt construction. Context Budgeting produces BudgetedContext.

---

ModelRoute

The immutable contract produced by the Model Router that declares which model capability should execute the prompt.

---

ToolRoute

The immutable contract produced by the Tool Router that declares which tool capability should execute.

---

4.3 Domain Responsibilities

Every core domain concept owns one responsibility.

Planner

Owns:

- Query understanding
- Planning decisions
- ExecutionPlan generation

Does not own:

- Retrieval
- Budgeting
- Routing
- Prompt construction
- Execution

---

ExecutionPlan

Owns:

- Planner decisions
- ProcessingGoal
- ResourceRequirements
- Complexity
- DecisionTrace

Does not own:

- Retrieved information
- Prompt text
- Runtime state
- Models
- Tools
- Results

---

Context Budgeting

Owns:

- Token budgeting
- Context prioritization
- Context trimming

Does not own:

- Retrieval
- Planning
- Prompt construction

---

Prompt Builder

Owns:

- Prompt formatting
- Prompt composition

Does not own:

- Planning
- Budgeting
- Retrieval

---

Model Router

Owns:

- Model selection

Does not own:

- Planning
- Retrieval
- Prompt generation

---

Tool Router

Owns:

- Tool selection

Does not own:

- Planning
- Context generation

---

4.4 Domain Contracts

Communication between architectural layers occurs only through immutable domain contracts.

Current contracts include:

- ExecutionPlan
- RetrievedContext
- BudgetedContext
- Prompt
- ModelRoute
- ToolRoute

Future contracts should follow the same philosophy.

Contracts should be:

- immutable,
- deterministic,
- serializable,
- replayable,
- explainable.

---

4.5 Domain Boundaries

The Core Domain is completely independent of infrastructure.

The Core Domain never depends upon:

- language models,
- vector databases,
- embedding models,
- filesystems,
- networks,
- cloud providers,
- operating systems.

Infrastructure depends on the Core Domain.

The reverse dependency is prohibited.

---

4.6 Domain Invariants

The following invariants must always hold.

Planning precedes execution.

Execution never modifies planner decisions.

---

ExecutionPlan is immutable.

Once created, planner decisions cannot change.

---

Responsibilities remain singular.

Every domain object owns exactly one responsibility.

---

Domain objects represent meaning.

They do not represent implementation details.

---

Downstream components consume decisions.

They never reinterpret planner intent.

---

Context is budgeted before prompt construction.

Prompt construction never receives unbudgeted context.

---

Every architectural decision should be explainable.

Opaque planner behaviour is considered an architectural defect.

---

Domain objects remain deterministic.

Identical inputs should produce identical domain outputs whenever possible.

---

4.7 Ownership Matrix

Domain Object| Owner| Primary Consumers
Planner| Planning Layer| ExecutionPlan Builder
ExecutionPlan| Planner| Context Budgeting, Prompt Builder, Routers
DecisionTrace| Planner| Observability, Debugging
Retriever| Retrieval Layer| Context Budgeting
BudgetedContext| Context Budgeting| Prompt Builder
Prompt| Prompt Builder| Model Router
ModelRoute| Model Router| Execution Layer
ToolRoute| Tool Router| Execution Layer
Model Selection| Model Router| Execution Layer
Tool Selection| Tool Router| Execution Layer

Ownership should remain explicit throughout the architecture.

No responsibility should have multiple owners.

---

4.8 Future Evolution

The Core Domain should evolve through extension rather than redesign.

Future capabilities such as:

- Web Search
- Database Access
- Image Processing
- Audio Processing
- Multi-Agent Coordination
- Cloud Execution

should integrate by extending existing contracts rather than replacing them.

The objective is long-term architectural stability.

---

Summary

The Core Domain is the conceptual foundation of the AI Ecosystem.

It defines the language, responsibilities, contracts, ownership, and invariants that every architectural component follows.

Implementation details may evolve.

The Core Domain should remain stable across future versions of the project.