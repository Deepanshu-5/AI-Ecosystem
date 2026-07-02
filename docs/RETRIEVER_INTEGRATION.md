# RETRIEVER_INTEGRATION.md

Version: 1.0
Status: Architecture Under Review
Scope: Retriever Integration
Authority: AI Ecosystem Engineering Team
Architecture Status: Under Design
Production Target: Production V1
Current Phase: Retriever Integration Architecture
Review Requirement: Architecture Review Required Before Implementation

---

# Overview

The Retriever Integration architecture defines how the Retriever subsystem communicates with the existing infrastructure while preserving the architectural boundaries established by the Domain Layer and the Integration Layer.

It provides the implementation contract for connecting the production-ready Retriever to the current Knowledge, Memory, and Session infrastructure.

The Retriever itself remains infrastructure independent.

All infrastructure communication occurs through the Integration Layer.

---

# Mission

Connect the Retriever subsystem to existing project infrastructure without introducing infrastructure dependencies into the Retriever.

The Retriever continues to operate exclusively on Domain contracts.

The Integration Layer performs all communication with infrastructure.

---

# Scope

This document covers:

- RetrieverIntegration
- Knowledge integration
- Memory integration
- Session integration
- Object translation
- Infrastructure communication
- Error translation
- Integration testing

This document does not redesign:

- Planner
- Retriever
- Context Budgeter
- Integration Layer
- Infrastructure implementations

---

# Current Infrastructure

The current project already contains infrastructure that must be reused.

Current infrastructure includes:

Knowledge Infrastructure

- Existing knowledge services
- Existing vector database
- Existing embedding pipeline
- Existing retrieval utilities

Memory Infrastructure

- Existing persistent memory components
- Existing memory services

Session Infrastructure

- Existing conversation memory
- Existing session management

The objective is to integrate with the existing infrastructure rather than replacing it.

Infrastructure reuse is preferred over new implementations whenever architectural boundaries can be preserved.

---

# Position in the Architecture

```text
Planner
      │
      ▼
Retriever
      │
      ▼

==========================
Retriever Integration
==========================

RetrieverIntegration

├── KnowledgeTranslator
├── MemoryTranslator
├── SessionTranslator

├── KnowledgeGateway
├── MemoryGateway
└── SessionGateway

==========================

Existing Infrastructure

Knowledge Services

Memory Services

Conversation Memory

Vector Database

Embedding Pipeline
```

The Retriever communicates only with RetrieverIntegration.

RetrieverIntegration owns all infrastructure communication.

---

# Responsibilities

RetrieverIntegration is responsible for:

- Coordinating infrastructure communication.
- Invoking Translators.
- Invoking Gateways.
- Translating infrastructure responses.
- Returning Domain objects.
- Translating infrastructure failures.
- Preserving Retriever contracts.

RetrieverIntegration owns integration only.

---

# Non-Responsibilities

RetrieverIntegration never performs:

Business Logic

- Retrieval decisions
- Planning
- Context budgeting
- Prompt construction

Translation

- Object mapping

Infrastructure Communication

- Direct database access
- Vector search implementation
- API implementation

Validation

- Domain validation
- Business rule validation

These responsibilities belong to other architectural components.

---

# Integration Goals

The Production V1 integration must satisfy the following goals.

Goal 1

The Retriever remains infrastructure independent.

---

Goal 2

Existing infrastructure is reused.

---

Goal 3

Infrastructure communication is isolated.

---

Goal 4

Translation remains deterministic.

---

Goal 5

The Retriever public contracts remain unchanged.

---

Goal 6

Future infrastructure replacements require modifications only inside the Integration Layer.

---

# Current Status

Status

Architecture Under Design

Implementation

Not Started

Architecture Review

Pending

Production Status

Not Production Ready

Next Milestone

Retriever Integration Architecture Review

Implementation begins only after architecture approval.
---

# Integration Architecture

Retriever Integration follows the Integration Layer architecture.

It provides a deterministic bridge between the Retriever subsystem and the existing infrastructure.

RetrieverIntegration owns the complete retrieval workflow.

No other component coordinates retrieval.

---

# Architecture Overview

```text
                     DOMAIN

                 Retriever
                     │
                     ▼

             RetrieverIntegration
                     │
     ┌───────────────┼────────────────┐
     ▼               ▼                ▼

KnowledgeIntegration MemoryIntegration SessionIntegration

     │               │                │

KnowledgeTranslator  MemoryTranslator SessionTranslator

     │               │                │

KnowledgeGateway     MemoryGateway    SessionGateway

     │               │                │

=============================================

          Existing Infrastructure

Knowledge Services
Memory Services
Conversation Memory
Vector Database
Embedding Pipeline
```

Retriever communicates only with RetrieverIntegration.

RetrieverIntegration owns every downstream dependency.

---

# RetrieverIntegration

Purpose

Coordinate the complete retrieval workflow.

Responsibilities

- Receive retrieval requests.
- Coordinate KnowledgeIntegration.
- Coordinate MemoryIntegration.
- Coordinate SessionIntegration.
- Assemble RetrievedContext.
- Preserve Retriever contracts.
- Translate infrastructure failures.

RetrieverIntegration never:

- performs retrieval logic
- performs object translation
- communicates directly with infrastructure
- modifies RetrievedContext

RetrieverIntegration owns orchestration only.

---

# KnowledgeIntegration

Purpose

Coordinate knowledge retrieval.

Responsibilities

- Invoke KnowledgeTranslator.
- Invoke KnowledgeGateway.
- Return KnowledgeContext.

KnowledgeIntegration never:

- access infrastructure directly
- perform translation itself
- coordinate memory retrieval
- coordinate session retrieval

KnowledgeIntegration owns knowledge workflow only.

---

# MemoryIntegration

Purpose

Coordinate persistent memory retrieval.

Responsibilities

- Invoke MemoryTranslator.
- Invoke MemoryGateway.
- Return MemoryContext.

MemoryIntegration never:

- access infrastructure directly
- perform translation
- coordinate knowledge retrieval
- coordinate session retrieval

MemoryIntegration owns memory workflow only.

---

# SessionIntegration

Purpose

Coordinate conversational session retrieval.

Responsibilities

- Invoke SessionTranslator.
- Invoke SessionGateway.
- Return SessionContext.

SessionIntegration never:

- access infrastructure directly
- perform translation
- coordinate knowledge retrieval
- coordinate memory retrieval

SessionIntegration owns session workflow only.

---

# Translator Responsibilities

Each Translator owns object conversion only.

KnowledgeTranslator

Infrastructure Knowledge Object

↓

KnowledgeItem

MemoryTranslator

Infrastructure Memory Object

↓

MemoryEntry

SessionTranslator

Infrastructure Session Object

↓

SessionMessage

Translators never:

- access infrastructure
- perform orchestration
- perform business logic

Translation must remain deterministic.

---

# Gateway Responsibilities

Each Gateway owns infrastructure communication.

KnowledgeGateway

Responsible for:

- vector search
- knowledge retrieval
- document loading

MemoryGateway

Responsible for:

- persistent memory access

SessionGateway

Responsible for:

- conversation history
- session retrieval

Gateways never:

- perform translation
- coordinate workflows
- expose infrastructure models

---

# Dependency Rules

Dependencies always point downward.

```text
Retriever

↓

RetrieverIntegration

↓

KnowledgeIntegration
MemoryIntegration
SessionIntegration

↓

Translator

↓

Gateway

↓

Infrastructure
```

Reverse dependencies are prohibited.

Infrastructure never depends upon Domain.

Domain never depends upon Infrastructure.

---

# Architectural Invariants

The following invariants must always remain true.

- Retriever owns retrieval decisions.
- RetrieverIntegration owns orchestration.
- KnowledgeIntegration owns knowledge workflow.
- MemoryIntegration owns memory workflow.
- SessionIntegration owns session workflow.
- Translators own translation.
- Gateways own infrastructure communication.
- Infrastructure objects never enter the Domain Layer.
- Translation remains deterministic.
- Existing infrastructure is reused whenever possible.

Violation of any invariant requires Architecture Review.
---

# Retrieval Pipeline

Every retrieval request follows the same deterministic execution pipeline.

```text
Retriever

↓

RetrieverIntegration

↓

KnowledgeIntegration
MemoryIntegration
SessionIntegration

↓

Translator

↓

Gateway

↓

Existing Infrastructure

↓

Gateway

↓

Translator

↓

Integration

↓

RetrievedContext

↓

Retriever
```

The execution pipeline is mandatory.

No stage may be bypassed.

---

# End-to-End Flow

The complete retrieval lifecycle consists of six phases.

---

## Phase 1

Retriever initiates retrieval.

Inputs

- ExecutionPlan
- Query
- Session Identifier

RetrieverIntegration receives the request.

RetrieverIntegration performs no retrieval itself.

---

## Phase 2

RetrieverIntegration determines which retrieval workflows are required.

Example

Knowledge Required

↓

Execute KnowledgeIntegration

Memory Not Required

↓

Skip MemoryIntegration

Session Required

↓

Execute SessionIntegration

RetrieverIntegration coordinates only.

---

## Phase 3

Each Integration invokes its Translator.

The Translator converts Domain requests into Infrastructure requests.

Examples

Domain Query

↓

Knowledge Search Request

Session Identifier

↓

Infrastructure Session Request

Translation must preserve meaning.

---

## Phase 4

Each Gateway communicates with existing infrastructure.

KnowledgeGateway

↓

Existing Knowledge Service

↓

Vector Database

MemoryGateway

↓

Existing Memory Service

↓

Persistent Storage

SessionGateway

↓

Existing Conversation Memory

↓

Session Storage

Existing infrastructure remains unchanged.

Gateways adapt existing infrastructure.

They do not replace it.

---

## Phase 5

Infrastructure responses return through the reverse path.

Infrastructure Response

↓

Gateway

↓

Translator

↓

Integration

The Translator converts Infrastructure objects into Domain objects.

Examples

Infrastructure Document

↓

KnowledgeItem

Infrastructure Memory Record

↓

MemoryEntry

Infrastructure Session Record

↓

SessionMessage

---

## Phase 6

RetrieverIntegration assembles the final result.

KnowledgeContext

+

MemoryContext

+

SessionContext

↓

RetrievedContext

RetrievedContext is returned to the Retriever.

Only Domain contracts leave the Integration Layer.

---

# Infrastructure Mapping

Production V1 reuses the existing infrastructure.

Knowledge

Retriever

↓

KnowledgeIntegration

↓

KnowledgeTranslator

↓

KnowledgeGateway

↓

Existing Knowledge Service

↓

Vector Database

---

Memory

Retriever

↓

MemoryIntegration

↓

MemoryTranslator

↓

MemoryGateway

↓

Existing Memory Service

↓

Memory Storage

---

Session

Retriever

↓

SessionIntegration

↓

SessionTranslator

↓

SessionGateway

↓

Existing Conversation Memory

↓

Session Storage

No existing infrastructure should be rewritten.

Only adapters are introduced.

---

# Object Mapping

The following mappings are permitted.

Knowledge

Infrastructure Document

↓

KnowledgeItem

↓

KnowledgeContext

---

Memory

Infrastructure Memory Record

↓

MemoryEntry

↓

MemoryContext

---

Session

Infrastructure Session Record

↓

SessionMessage

↓

SessionContext

Infrastructure objects never leave the Integration Layer.

---

# Error Translation

Infrastructure exceptions remain inside the Integration Layer.

Examples

Database Failure

↓

KnowledgeIntegrationError

Memory Service Failure

↓

MemoryIntegrationError

Conversation Failure

↓

SessionIntegrationError

Infrastructure exceptions must never reach the Retriever.

---

# Validation

The Integration Layer performs structural validation only.

Examples

- Missing infrastructure fields
- Invalid response types
- Corrupted infrastructure payloads

Business validation remains the responsibility of the Retriever subsystem.

---

# Public Contracts

RetrieverIntegration exposes only Domain contracts.

Inputs

- ExecutionPlan
- Query
- Session Identifier

Outputs

- RetrievedContext

Infrastructure types remain internal implementation details.

---

# Determinism

The Retrieval Integration must be deterministic.

Identical

ExecutionPlan

+

Query

+

Session Identifier

+

Infrastructure State

↓

Produces identical RetrievedContext.

No hidden state.

No random behaviour.

No infrastructure objects may cross architectural boundaries.
---

# Project Structure

The Retriever Integration follows the Integration Layer architecture.

```text
integration/
│
├── integrations/
│   ├── retriever_integration.py
│   ├── knowledge_integration.py
│   ├── memory_integration.py
│   └── session_integration.py
│
├── translators/
│   ├── knowledge_translator.py
│   ├── memory_translator.py
│   └── session_translator.py
│
├── gateways/
│   ├── knowledge_gateway.py
│   ├── memory_gateway.py
│   └── session_gateway.py
│
└── exceptions.py
```

No additional files should be introduced unless approved through Architecture Review.

---

# File Responsibilities

## retriever_integration.py

Purpose

Coordinate the complete retrieval integration workflow.

Responsibilities

- Receive retrieval requests.
- Coordinate KnowledgeIntegration.
- Coordinate MemoryIntegration.
- Coordinate SessionIntegration.
- Assemble RetrievedContext.
- Return Domain contracts.

Must never:

- perform business logic
- communicate directly with infrastructure
- translate objects

---

## knowledge_integration.py

Purpose

Coordinate knowledge retrieval.

Responsibilities

- Invoke KnowledgeTranslator.
- Invoke KnowledgeGateway.
- Construct KnowledgeContext.
- Return KnowledgeContext.

Must never:

- access infrastructure directly
- perform translation
- coordinate memory
- coordinate session

---

## memory_integration.py

Purpose

Coordinate memory retrieval.

Responsibilities

- Invoke MemoryTranslator.
- Invoke MemoryGateway.
- Construct MemoryContext.
- Return MemoryContext.

Must never:

- access infrastructure directly
- perform translation
- coordinate knowledge
- coordinate session

---

## session_integration.py

Purpose

Coordinate session retrieval.

Responsibilities

- Invoke SessionTranslator.
- Invoke SessionGateway.
- Construct SessionContext.
- Return SessionContext.

Must never:

- access infrastructure directly
- perform translation
- coordinate knowledge
- coordinate memory

---

## knowledge_translator.py

Purpose

Translate between Knowledge infrastructure objects and Domain objects.

Responsibilities

Infrastructure Object

↓

KnowledgeItem

KnowledgeItem

↓

Infrastructure Object

Translator owns conversion only.

---

## memory_translator.py

Purpose

Translate between Memory infrastructure objects and Domain objects.

Responsibilities

Infrastructure Memory

↓

MemoryEntry

MemoryEntry

↓

Infrastructure Memory

Translator owns conversion only.

---

## session_translator.py

Purpose

Translate between Session infrastructure objects and Domain objects.

Responsibilities

Infrastructure Session

↓

SessionMessage

SessionMessage

↓

Infrastructure Session

Translator owns conversion only.

---

## knowledge_gateway.py

Purpose

Adapt the existing Knowledge infrastructure.

Responsibilities

- Call existing Knowledge services.
- Execute retrieval.
- Return infrastructure objects.

Must never

- perform translation
- perform business logic
- construct Domain objects

---

## memory_gateway.py

Purpose

Adapt the existing Memory infrastructure.

Responsibilities

- Read persistent memory.
- Return infrastructure objects.

Must never

- perform translation
- perform business logic

---

## session_gateway.py

Purpose

Adapt the existing Conversation Memory infrastructure.

Responsibilities

- Retrieve session history.
- Return infrastructure objects.

Must never

- perform translation
- perform business logic

---

## exceptions.py

Purpose

Define Retriever Integration exceptions.

Responsibilities

Translate infrastructure failures into Integration exceptions.

Infrastructure exceptions must never leave the Integration Layer.

---

# Implementation Order

Implementation should follow the following sequence.

Step 1

exceptions.py

↓

Step 2

Gateways

↓

Step 3

Translators

↓

Step 4

KnowledgeIntegration

↓

Step 5

MemoryIntegration

↓

Step 6

SessionIntegration

↓

Step 7

RetrieverIntegration

↓

Step 8

Unit Tests

↓

Step 9

Integration Tests

↓

Step 10

End-to-End Validation

Each step should pass validation before the next begins.

---

# Testing Strategy

The Retriever Integration requires four levels of testing.

---

## Translator Tests

Verify

- Infrastructure → Domain translation
- Domain → Infrastructure translation
- Deterministic conversion

---

## Gateway Tests

Verify

- Existing services are called correctly.
- Infrastructure failures are translated.
- Expected infrastructure responses are returned.

Gateways may use mocks where appropriate.

---

## Integration Tests

Verify

- RetrieverIntegration orchestration.
- KnowledgeIntegration workflow.
- MemoryIntegration workflow.
- SessionIntegration workflow.
- Correct translator usage.
- Correct gateway usage.

---

## End-to-End Tests

Verify

```text
Retriever

↓

RetrieverIntegration

↓

Existing Infrastructure

↓

Retriever
```

The complete pipeline must preserve all architectural boundaries.

---

# Documentation Requirements

Every public class must document

- Purpose
- Responsibilities
- Consumers
- Dependencies
- Invariants

Every public method must document

- Parameters
- Returns
- Raises
- Side Effects

Documentation is part of the implementation.

---

# Implementation Notes

Production V1 must reuse existing project infrastructure.

Existing services must not be rewritten.

Existing infrastructure must be adapted through Gateways.

Object conversion must occur only inside Translators.

Retriever contracts must remain unchanged.

Implementation should favour reuse over replacement.
---

# Future Evolution

The following capabilities are intentionally deferred beyond Production V1.

Future enhancements must preserve the architecture defined in this document.

Possible future capabilities include:

- Multiple Knowledge providers
- Multiple Memory providers
- Multiple Session providers
- Hybrid Knowledge retrieval
- Distributed infrastructure
- Cloud infrastructure
- Provider failover
- Infrastructure health monitoring
- Parallel infrastructure communication
- Request batching
- Response caching
- Telemetry integration

These capabilities extend the Retriever Integration.

They must not redesign it.

The responsibilities of:

- RetrieverIntegration
- KnowledgeIntegration
- MemoryIntegration
- SessionIntegration
- Translators
- Gateways

must remain unchanged.

---

# Modification Policy

The Retriever Integration architecture is considered frozen after approval.

The following changes are permitted without Architecture Review:

- bug fixes
- documentation improvements
- implementation refinements
- infrastructure-specific improvements
- performance optimizations
- backward-compatible provider support

The following changes require Architecture Review:

- new architectural components
- responsibility changes
- dependency rule changes
- communication flow changes
- public contract changes
- ownership changes

Implementation must never redefine architecture.

---

# AI Implementation Instructions

If you are an AI assistant implementing Retriever Integration:

1.

Read the following documents before writing code.

- AI_ECOSYSTEM_BOOTSTRAP.md
- PROJECT_BLUEPRINT.md
- ENGINEERING_CONSTITUTION.md
- IMPLEMENTATION_SPEC.md
- INTEGRATION_LAYER.md
- RETRIEVER.md
- RETRIEVER_INTEGRATION.md

These documents are the authoritative engineering source.

---

2.

Treat this architecture as frozen.

Do not redesign:

- Retriever
- Integration Layer
- responsibilities
- dependencies
- communication flow
- public contracts

Implement only.

---

3.

Reuse existing infrastructure.

Do not replace existing:

- Knowledge services
- Memory services
- Conversation memory
- Vector database integration
- Embedding pipeline

Adapters must wrap existing infrastructure.

Existing infrastructure should remain unchanged unless required for compatibility.

---

4.

Implement only the required files.

Do not introduce:

- dependency injection frameworks
- service locators
- plugin systems
- registries
- factories
- speculative abstractions

unless explicitly required by future architecture.

---

5.

Maintain strict responsibility boundaries.

Retriever

↓

RetrieverIntegration

↓

KnowledgeIntegration
MemoryIntegration
SessionIntegration

↓

Translator

↓

Gateway

↓

Existing Infrastructure

Responsibilities must never overlap.

---

6.

If architectural ambiguity exists,

do not invent a solution.

Instead report:

Architecture Question

Problem

Impact

Recommendation

Pause implementation until architecture is clarified.

---

7.

Implementation is complete only when:

- architecture preserved
- existing infrastructure reused
- translators implemented
- gateways implemented
- integrations implemented
- unit tests passing
- integration tests passing
- end-to-end tests passing
- documentation complete

Only then may Retriever Integration be considered Production Ready.

---

# Deliverables

Implementation must provide:

integration/

- retriever_integration.py
- knowledge_integration.py
- memory_integration.py
- session_integration.py

translators/

- knowledge_translator.py
- memory_translator.py
- session_translator.py

gateways/

- knowledge_gateway.py
- memory_gateway.py
- session_gateway.py

exceptions.py

Unit Tests

Integration Tests

End-to-End Tests

Documentation

Every file should be returned separately.

---

# Definition of Done

Retriever Integration is complete only when:

✓ Existing infrastructure reused

✓ Retriever unchanged

✓ Domain contracts preserved

✓ Infrastructure isolated

✓ Translators deterministic

✓ Gateways isolated

✓ Integration Components coordinate only

✓ Unit tests passing

✓ Integration tests passing

✓ End-to-End tests passing

✓ Architecture Review PASS

✓ Implementation Review PASS

✓ Integration Review PASS

Only then may Retriever Integration be merged.

---

# Engineering Outcome

Retriever Integration establishes the first production implementation of the Integration Layer architecture.

It demonstrates how Domain subsystems communicate with Infrastructure while preserving complete architectural independence.

This implementation becomes the reference implementation for future subsystem integrations including:

- Context Budgeter
- Prompt Builder
- Model Router
- Tool Router

Future subsystem integrations should follow the same architectural pattern established here.

---

# Current Status

Status

Architecture Frozen

Implementation

Ready to Begin

Production Status

Not Production Ready

Next Milestone

Retriever Integration Implementation
