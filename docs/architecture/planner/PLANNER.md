Version: 1.0

Status: Production Ready

Architecture Status: Frozen

Production Target: Production V1

Current Phase: Production V1 Freeze

Review Requirement:
Architecture Review Required Before Modification

---

# PLANNER.md

## Overview

The Planner is the decision engine of the AI Ecosystem Control Plane.

Its responsibility is to analyze a raw user query and deterministically produce an immutable `ExecutionPlan` that downstream components can execute.

The Planner performs **decision-making only**. It never retrieves data, constructs prompts, executes tools, or calls language models.

The Planner is designed to be deterministic, infrastructure-independent, and easily testable.

---

# Mission

Transform a raw user query into an immutable `ExecutionPlan`.

The Planner answers:

* What kind of request is this?
* How complex is it?
* Which resources are required?
* Why were these decisions made?

The Planner does **not** answer the user's question.

---

# Scope

## Responsibilities

* Normalize queries
* Analyze queries
* Classify Processing Goal
* Estimate Complexity
* Determine Resource Requirements
* Generate Decision Trace
* Build immutable ExecutionPlan
* Validate ExecutionPlan

## Non-Responsibilities

The Planner never:

* Retrieves knowledge
* Retrieves memory
* Retrieves session context
* Calls LLMs
* Builds prompts
* Executes tools
* Chooses models
* Performs infrastructure operations

---

# Architecture

```text
                  User Query
                      │
                      ▼
              QueryAnalyzer
                      │
                      ▼
             PlanningContext
                      │
                      ▼
              PlannerBuilder
                      │
                      ▼
             PlannerValidator
                      │
                      ▼
               ExecutionPlan
```

---

# Component Overview

## QueryAnalyzer

Purpose

Analyze a normalized query and produce a PlanningContext.

Responsibilities

* Query normalization
* ProcessingGoal classification
* Complexity estimation
* Resource requirement determination
* Decision trace generation

Output

PlanningContext

---

## PlanningContext

Internal immutable object.

Purpose

Carry intermediate planning decisions before building the final ExecutionPlan.

Consumers

* PlannerBuilder

---

## PlannerBuilder

Purpose

Assemble an immutable ExecutionPlan from PlanningContext components.

Responsibilities

* Build ExecutionPlan
* Invoke PlannerValidator

Does not perform inference or validation logic itself.

---

## PlannerValidator

Purpose

Ensure every ExecutionPlan satisfies architectural rules.

Validation Categories

* Structural
* Logical
* Semantic

Rejects invalid plans before they enter the execution pipeline.

---

## ExecutionPlan

The only public contract exposed by the Planner.

Contains

* ProcessingGoal
* Complexity
* ResourceRequirements
* DecisionTrace
* Schema Version

Immutable after construction.

---

# Domain Model

## ProcessingGoal

Represents the primary purpose of a query.

Values

* GENERAL
* KNOWLEDGE
* MEMORY
* SESSION
* DOCUMENT
* CODE

Only one ProcessingGoal exists per ExecutionPlan.

---

## Complexity

Represents execution complexity.

Values

* LOW
* MEDIUM
* HIGH

Used by downstream routing systems.

---

## ResourceRequirements

Determines which ecosystem resources are required.

Fields

* knowledge
* memory
* session

Each field is an independent boolean.

Multiple resources may be requested simultaneously.

---

## DecisionTrace

Human-readable explanation describing why the Planner reached each decision.

Used for debugging and explainability.

---

# Planner Pipeline

```text
Raw Query
    │
    ▼
Normalize Query
    │
    ▼
Determine ProcessingGoal
    │
    ▼
Estimate Complexity
    │
    ▼
Determine Resource Requirements
    │
    ▼
Generate Decision Trace
    │
    ▼
Create PlanningContext
    │
    ▼
Build ExecutionPlan
    │
    ▼
Validate ExecutionPlan
```

---

# Decision Rules

## ProcessingGoal

Priority

1. DOCUMENT
2. MEMORY
3. SESSION
4. CODE
5. KNOWLEDGE
6. GENERAL

The first matching rule wins.

---

## Complexity

LOW

Simple lookup or definition.

MEDIUM

Comparison, explanation, summarization.

HIGH

Planning, architecture, design, optimization, multi-step reasoning.

---

## Resource Requirements

Determined independently.

Knowledge

Requested for factual, document, and code queries.

Memory

Requested for persistent user information.

Session

Requested for previous conversation context.

---

# AI Implementation Instructions

This section is directed at AI assistants and future maintainers.

## Frozen Components

The following are **frozen for Production V1** and must never be modified without explicit architecture review:

- **ExecutionPlan contract:** Immutable, single public output of the Planner. Any field addition, removal, or rename requires architecture review.
- **ProcessingGoal values:** GENERAL, KNOWLEDGE, MEMORY, SESSION, DOCUMENT, CODE. Do not add, remove, or rename values without architecture review.
- **Complexity values:** LOW, MEDIUM, HIGH. Do not modify without architecture review.
- **ResourceRequirements structure:** (knowledge, memory, session) boolean fields. Do not modify without architecture review.
- **DecisionTrace ownership:** Always owned by Planner. Never transfer to downstream components.
- **Planner non-responsibilities:** The Planner never retrieves, budgets context, constructs prompts, routes tools, routes models, or executes work. This boundary is absolute.
- **Dependency direction:** Planner depends on nothing. Planner is the root of the Control Plane. Do not introduce dependencies upward or to peer systems.

## Permitted Changes

- **Bug fixes:** Repair incorrect behavior within frozen contracts.
- **Documentation improvements:** Clarify existing design without changing architecture.
- **Backward-compatible refinements:** Optimize implementation without changing public contracts or behavior.
- **Test additions:** Expand test coverage without modifying domain logic.

## Prohibited Changes

- **Do not redesign the Planner:** Only bug fixes and backward-compatible improvements are allowed.
- **Do not introduce new Planner responsibilities:** New capabilities must be designed as separate subsystems.
- **Do not modify public contracts:** ExecutionPlan, ProcessingGoal, Complexity, ResourceRequirements, and DecisionTrace are immutable.
- **Do not add infrastructure dependencies:** The Planner must remain deterministic, testable, and infrastructure-independent.
- **Do not introduce speculative features:** Only implement Production V1 requirements.

If a change requires breaking the frozen architecture, stop and raise a formal Architecture Question instead of silently modifying the design.

---

# Public API

```python
QueryAnalyzer.analyze(query: str) -> PlanningContext

PlannerBuilder.build(...) -> ExecutionPlan

PlannerValidator.validate(execution_plan) -> None
```

---

# Design Principles

The Planner follows:

* Deterministic behavior
* Single Responsibility Principle
* Immutable domain objects
* Infrastructure independence
* No hidden side effects
* Explicit validation
* Stable public contracts
* Explainable decisions

---

# Project Structure

```text
planner/
├── __init__.py
├── complexity.py
├── decision_trace.py
├── exceptions.py
├── execution_plan.py
├── planner_builder.py
├── planner_validator.py
├── planning_context.py
├── processing_goal.py
├── query_analyzer.py
└── resource_requirements.py
```

---

# Testing

The Planner has been verified using:

* Unit Tests
* Component Tests
* Builder Tests
* Validator Tests
* QueryAnalyzer Tests
* End-to-End Pipeline Tests

Total Test Status

All tests passing.

---

# Future Evolution

The following capabilities are intentionally deferred beyond Production V1.

* Confidence scoring
* Ambiguity detection
* Hybrid rule + LLM planning
* Multi-goal planning
* Planner analytics
* Adaptive planning strategies

These features will be introduced without breaking the existing ExecutionPlan contract.

---

# Current Status

Status

Production Ready (V1)

Architecture

Frozen

Modification Policy

Only bug fixes and backward-compatible improvements are permitted.

Breaking architectural changes require a formal architecture review.
