# AI Ecosystem — Sprint Template

Version: 1.0
Status: Active
Scope: Individual Engineering Sprint

---

## 1. Sprint Information

**Sprint ID:**

**Sprint Name:**

**Status:** Planned / In Progress / Review / Completed

**Architecture Status:**

- [ ] Under Design
- [ ] Architecture Frozen

**Dependencies:**

List previously completed sprints or modules required before this sprint.

---

## 2. Objective

Describe the purpose of this sprint in one concise paragraph.

The objective must define **what** is being implemented, **not how** it will be implemented.

Example:

> Implement the immutable ExecutionPlan domain contract used by the Planner to communicate planning decisions to downstream components.

---

## 3. Architectural Context

Summarize only the architectural context required for this sprint.

Do not repeat the Engineering Constitution.

Reference the existing architecture.

Example:

- ExecutionPlan is the immutable output of the Planner.
- Architecture has already been reviewed and frozen.
- This sprint must not introduce architectural changes.

---

## 4. Scope

Clearly define everything that is allowed in this sprint.

Example:

- Implement immutable domain objects.
- Implement builder.
- Implement validator.
- Implement domain exceptions.
- Implement deterministic serialization.

Everything not listed is considered out of scope.

---

## 5. Out of Scope

Explicitly define what must NOT be implemented.

Example:

- Planner logic
- Retrieval
- Context Budgeting
- Prompt Builder
- Model Routing
- Tool Routing
- Memory Retrieval
- Session Retrieval
- MCP Integration
- Logging
- Metrics
- Configuration
- Dependency Injection

---

## 6. Frozen Architectural Decisions

List only the architectural decisions that are relevant to this sprint.

Example:

- Domain objects are immutable.
- Builder orchestrates construction.
- Validator performs deterministic validation.
- Validation occurs before object creation completes.
- Domain layer must remain infrastructure independent.

No architectural changes are permitted during implementation.

---

## 7. Implementation Requirements

Implementation must follow:

- ENGINEERING_CONSTITUTION.md
- IMPLEMENTATION_SPEC.md

Additional sprint-specific requirements:

- Fully typed.
- Frozen dataclasses.
- Deterministic behaviour.
- Serializable.
- Replayable.
- No speculative abstractions.
- Minimal public API.

---

## 8. Files To Implement

List only the files included in this sprint.

Example:

```
planner/
    exceptions.py
    decision_trace.py
```

Do not modify unrelated modules.

---

## 9. Deliverables

Return:

- Complete source code.
- Complete docstrings.
- Type hints.
- Public API.

Return every file separately.

Do not redesign architecture.

---

## 10. Self Review

Before submitting, verify:

- [ ] Mission preserved
- [ ] Architecture preserved
- [ ] Single Responsibility maintained
- [ ] Ownership explicit
- [ ] No hidden dependencies
- [ ] Domain independent from infrastructure
- [ ] Immutable where required
- [ ] Validation complete
- [ ] Documentation complete
- [ ] Fully typed
- [ ] Deterministic
- [ ] Serializable
- [ ] Replayable
- [ ] Testable in isolation

If any check fails, implementation is incomplete.

---

## 11. Architecture Questions

If implementation reveals an architectural uncertainty, do not invent a solution.

Instead report:

### Architecture Question

**Problem**

Describe the uncertainty.

**Impact**

Explain why it affects implementation.

**Recommendation**

Provide one or more possible architectural solutions.

Stop implementation until architecture is clarified.

---

## 12. Implementation Observations

After implementation, optionally provide:

- Documentation improvements
- Simplifications
- Refactoring opportunities
- Performance observations

These observations must not change the implementation.

They are suggestions only.

---

## 13. Review Checklist

Implementation will undergo three reviews.

### Static Review

Verify:

- Syntax
- Typing
- Imports
- Style
- Documentation

---

### Architecture Review

Verify:

- Matches frozen architecture
- No architectural drift
- Responsibilities preserved
- No new coupling
- No speculative abstractions

---

### Integration Review

Verify:

- Compatible with existing modules
- Stable public API
- No unnecessary dependencies
- Ready for downstream integration

---

## 14. Completion Criteria

A sprint is complete only when:

- Implementation is finished.
- Static Review passes.
- Architecture Review passes.
- Integration Review passes.
- Quality Gates pass.
- Documentation is complete.
- Architecture remains unchanged.
- Final merge is approved.

Only then may the sprint be marked as **MERGED**.

---

## 15. Sprint Outcome

Record the final result.

**Status:**

- NOT STARTED
- IN PROGRESS
- REVIEW REQUIRED
- CHANGES REQUESTED
- APPROVED
- MERGED

**Record:**

- Merge Date
- Reviewer
- Notes
- Follow-up Tasks (if any)

---

## Sprint Philosophy

Each sprint should produce one cohesive, production-ready increment.

Architecture is designed before implementation.

Implementation follows the architecture.

Review verifies the implementation.

Merge finalizes the sprint.

Never redesign architecture during implementation.

---

*Owned by: Engineering Standards*

*Consumed by: All contributors, all sprint authors, all reviewers*

*Last updated: 2026-06-24*
