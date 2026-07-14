8. Contributor Protocol

The AI Ecosystem is designed to be developed by multiple contributors over a long period of time.

Contributors may include:

- Human engineers
- AI assistants
- Future maintainers
- Future versions of the project owner

This protocol defines the behavioural expectations required to preserve architectural integrity, implementation quality, and long-term maintainability.

Every contributor should treat the architecture as a shared engineering asset rather than personal code.

---

8.1 Primary Responsibility

Every contributor has one primary responsibility.

Preserve the architecture.

Implementation exists to realize architecture.

It must never redefine architecture.

Whenever implementation conflicts with architecture, implementation should stop until the architectural conflict has been resolved.

---

8.2 Required Reading Order

Before modifying the project, contributors should review information in the following order.

1. PROJECT_BLUEPRINT.md

Understand the project.

---

2. ENGINEERING_CONSTITUTION.md

Understand engineering philosophy.

---

3. IMPLEMENTATION_SPEC.md

Understand implementation standards.

---

4. Current Sprint

Understand current objectives.

---

5. Relevant Source Code

Only after understanding the project context.

Code should never become the primary source of architectural truth.

---

8.3 Required Thinking Process

Every engineering task should follow the same reasoning process.

Problem

↓

Mission Analysis

↓

Architecture Review

↓

Responsibility Analysis

↓

Validation

↓

Implementation

↓

Review

↓

Merge

Implementation should never begin immediately after receiving a request.

Thinking precedes coding.

---

8.4 Internal Validation

Before proposing any architectural or implementation decision, contributors should internally verify:

Mission Alignment

Does this support the project objectives?

---

Architectural Consistency

Does this preserve the current architecture?

---

Single Responsibility

Does every component own one responsibility?

---

No Regret Rule

Will this remain valuable after future evolution?

---

Complexity

Does this simplify or complicate the system?

---

Evidence

Is this recommendation supported by measurements or architectural reasoning?

Only validated conclusions should be presented.

If multiple valid solutions remain, the trade-offs should be explained explicitly.

---

8.5 Handling Uncertainty

Whenever uncertainty exists, contributors should classify it.

Implementation Question

Implementation is unclear.

Architecture remains stable.

Proceed after clarification.

---

Architecture Question

Architecture is uncertain.

Stop implementation.

Review architecture first.

---

Mission Conflict

The requested change conflicts with project objectives.

Stop.

Architectural review is required.

---

No contributor should invent architecture to continue implementation.

---

8.6 Architecture Preservation

Contributors should never:

- redesign frozen architecture,
- silently modify responsibilities,
- change ownership,
- introduce speculative abstractions,
- merge unrelated responsibilities,
- optimize without evidence.

Architectural stability is more valuable than rapid feature development.

---

8.7 Decision Hierarchy

When decisions conflict, use the following priority.

Mission

↓

Architecture

↓

Core Domain

↓

Implementation Standards

↓

Sprint Objectives

↓

Implementation

↓

Developer Convenience

Higher levels always override lower levels.

---

8.8 Communication Standards

Engineering communication should be:

- objective,
- precise,
- evidence-based,
- architecture-focused,
- technically accurate.

Recommendations should explain:

- why,
- expected impact,
- architectural consequences,
- future evolution implications.

Speculation should be identified clearly.

---

8.9 AI Assistant Behaviour

AI assistants contributing to the project should:

- reason before implementation,
- validate internally before responding,
- preserve architectural consistency,
- avoid hallucinating missing architecture,
- avoid speculative features,
- ask architecture questions when uncertainty exists,
- prefer deterministic solutions,
- optimize only after measurement,
- follow the Engineering Constitution.

AI should function as an engineering collaborator rather than an autonomous architect.

---

8.10 Human Contributor Behaviour

Human contributors should:

- understand architecture before coding,
- preserve ubiquitous language,
- maintain explicit ownership,
- document architectural decisions,
- review before merging,
- measure before optimizing,
- avoid introducing technical debt for short-term convenience.

Every change should strengthen the architecture.

---

8.11 Review Expectations

Every contributor should review their own work before requesting review from others.

Minimum review includes:

- architectural consistency,
- responsibility validation,
- implementation correctness,
- documentation,
- testing readiness,
- maintainability.

Review is considered part of implementation rather than a separate activity.

---

8.12 Long-Term Stewardship

The AI Ecosystem is intended to evolve over many years.

Every contributor is responsible for leaving the project in a better state than they found it.

Examples include:

- simplifying architecture,
- improving documentation,
- removing unnecessary complexity,
- strengthening abstractions,
- increasing determinism,
- improving observability.

Small continuous improvements are preferred over periodic redesigns.

---

Summary

The Contributor Protocol defines how people and AI systems collaborate while preserving the architectural integrity of the AI Ecosystem.

It establishes a common engineering process, a shared decision hierarchy, and consistent expectations for reasoning, implementation, validation, and review.

Its purpose is not to restrict contributors, but to ensure that every contribution strengthens the project rather than introducing architectural drift.