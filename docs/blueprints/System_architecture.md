2. System Architecture

Architecture Overview

The AI Ecosystem is designed as a layered control plane that sits between users and language models.

Instead of forwarding user requests directly to an LLM, the ecosystem performs a sequence of deterministic planning, retrieval, budgeting, and routing operations before inference begins.

Every layer has a single responsibility.

Information flows downward.

Decisions never flow upward.

Execution never changes planner decisions.

The system follows the principle:

«Plan first. Execute second.»

---

High-Level Architecture

User
        │
        ▼
Intent & Planning Layer
        │
        ▼
Information Planning
        │
        ▼
Knowledge Retrieval
Memory Retrieval
Session Retrieval
        │
        ▼
Context Budgeting
        │
        ▼
Prompt Construction
        │
        ▼
Tool Routing
        │
        ▼
Model Routing
        │
        ▼
Language Model
        │
        ▼
Response

Every stage reduces uncertainty for the next stage.

No stage should perform work that belongs to another stage.

---

Architectural Layers

The system is divided into independent architectural layers.

Each layer owns exactly one responsibility.

---

Knowledge Layer

Purpose

Persistent factual information.

Responsibilities

- Document ingestion
- Extraction
- Chunking
- Embedding
- Storage
- Retrieval
- Reranking

Current Components

- Extractor
- Chunker
- Embedder
- ChromaDB
- Retriever
- Reranker

Output

Relevant factual knowledge.

The Knowledge Layer never stores user-specific memory.

---

Memory Layer

Purpose

Persistent user knowledge.

Responsibilities

- Memory extraction
- Memory filtering
- Deduplication
- Storage
- Retrieval

Output

Relevant long-term user memory.

Memory represents stable user information.

Memory never replaces factual knowledge.

---

Session Layer

Purpose

Short-term conversational continuity.

Responsibilities

- Session management
- Threshold detection
- Incremental summarization
- Session retrieval

Output

Recent conversational context.

The Session Layer exists to preserve continuity without continuously increasing prompt size.

---

Planner Layer

Purpose

Determine how a request should be processed.

Responsibilities

- Query understanding
- ProcessingGoal determination
- Resource requirements
- Complexity estimation
- DecisionTrace generation
- ExecutionPlan construction

Output

ExecutionPlan

The Planner never performs retrieval.

The Planner produces decisions.

---

Context Budgeting Layer

Purpose

Optimize context before inference.

Responsibilities

- Token counting
- Budget allocation
- Priority enforcement
- Context trimming
- Context ordering

Priority

1. Critical Knowledge

2. Critical Memory

3. Session Context

4. Supporting Information

Output

Budgeted context.

The Budgeter never retrieves information.

---

Prompt Construction Layer

Purpose

Transform structured planner output into the final model prompt.

Responsibilities

- Prompt assembly
- Context formatting
- System instruction composition

The Prompt Builder never performs planning.

It consumes planner output.

---

Tool Routing Layer

Purpose

Determine whether external tools are required.

Future Responsibilities

- Tool selection
- Tool sequencing
- Tool execution planning

This layer remains intentionally minimal during Production V1.

---

Model Routing Layer

Purpose

Select the most appropriate language model.

Future Responsibilities

- Model selection
- Cost optimization
- Latency optimization
- Fallback strategy

Current Default

qwen2.5:1.5b

Future routing may select different models depending on ExecutionPlan complexity.

---

Dependency Rules

Dependencies always point downward.

Example

Planner

↓

Budgeter

↓

Prompt Builder

↓

Router

↓

LLM

Lower layers never influence higher-layer decisions.

The architecture intentionally prevents circular dependencies.

---

Architectural Boundaries

Each layer owns one responsibility.

Responsibilities never overlap.

Examples

Planner

Determines what should happen.

Budgeter

Determines how much context is available.

Prompt Builder

Determines how information is formatted.

Model Router

Determines which model executes.

Execution Layer

Produces the final response.

Each layer consumes the output of the previous layer without modifying its decisions.

---

Information Flow

Information moves through the system in stages.

Raw Request

↓

Planning

↓

Information Retrieval

↓

Context Optimization

↓

Prompt Construction

↓

Execution

↓

Response

Every stage reduces ambiguity.

Every stage prepares information for the next stage.

No stage should duplicate work performed earlier.

---

Control Plane Philosophy

The AI Ecosystem is fundamentally a control plane.

Language models are execution engines.

Planning, budgeting, routing, retrieval, and orchestration remain the responsibility of the ecosystem.

As the system evolves, more intelligence moves into the control plane while language models perform increasingly focused inference.

This separation reduces token usage, improves determinism, simplifies provider replacement, and enables long-term evolution.

---

Hardware Constraints

Current Target

- Intel i7-13620H
- 16 GB RAM
- Windows
- CPU-only inference

The architecture must remain practical under these constraints.

Future cloud or hybrid deployments extend the architecture rather than replacing it.

---

Performance Philosophy

Optimization follows measurement.

Current measurements show:

- Retrieval is not the bottleneck.
- Memory retrieval is not the bottleneck.
- Prompt construction is effectively negligible.
- Cold-start latency is primarily model loading.

Engineering effort therefore prioritizes architectural intelligence over premature optimization.

Every optimization must be justified through measurable improvement.

---

Architectural Invariants

The following invariants must always hold.

- Planning occurs before execution.
- Domain remains independent from infrastructure.
- Layers communicate only through defined contracts.
- Responsibilities remain singular.
- Planner output is immutable.
- Execution never modifies planning decisions.
- Context is always budgeted before inference.
- Optimization is measurement driven.
- Future evolution extends rather than redesigns the architecture.

These invariants define the long-term stability of the AI Ecosystem.