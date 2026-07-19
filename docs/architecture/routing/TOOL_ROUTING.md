Version: 1.0

Status: Production Ready

Architecture Status: Frozen

Production Target: Production V1

Current Phase: Production V1 Freeze

Review Requirement:
Architecture Review Required Before Modification

---

# Tool Routing V1 Architecture

AI Implementation Notice:
Implementations must follow ENGINEERING_CONSTITUTION.md and IMPLEMENTATION_SPEC.md. Preserve Tool Routing ownership, immutable public contracts (ExecutionPlan, ToolRoute), and dependency direction. Do not duplicate governance or implementation rules; reference the authoritative documents listed above.


# 1. Purpose

Tool Routing is a deterministic Control Plane subsystem.

Its sole V1 responsibility is to select semantic information-access
capabilities explicitly required by an existing Planner decision.

``` text
ExecutionPlan
↓
ToolRouter
↓
ToolRoute
```

It does not execute tools, resolve runtime functions, inspect MCP
exposure, discover tools, construct arguments, or reinterpret query
semantics.

V1 is limited to decisions exactly derivable from frozen Planner
contracts.

# 2. Mission Alignment

The AI Ecosystem makes intelligent decisions before expensive execution.
Tool Routing converts Planner-owned information requirements into an
explicit capability decision before future execution integration.

It exists to make required capabilities explicit, prevent unnecessary
capability execution, preserve infrastructure independence, and provide
a deterministic downstream contract.

# 3. Current Contract Reality and Scope

The current infrastructure exposes memory read, memory write, session
processing/write, composite legacy context acquisition, and health
probing.

The frozen Planner preserves `ProcessingGoal`, `Complexity`,
`ResourceRequirements`, and `DecisionTrace`.

`ResourceRequirements` declares whether knowledge, memory, and session
information must be consulted. The Planner does not preserve canonical
read/write/action intent.

Therefore `ExecutionPlan` cannot deterministically distinguish memory
recall from memory write, or session access from session mutation,
without downstream semantic re-analysis.

Tool Routing must not re-analyze raw query text, parse `DecisionTrace`,
overload `ProcessingGoal`, or reinterpret `ResourceRequirements` as a
universal action contract.

V1 routes exactly:

``` text
KNOWLEDGE_ACCESS
MEMORY_ACCESS
SESSION_ACCESS
```

Deferred pending an operation-semantic authority review:

-   memory write;
-   session write/process;
-   health/probe;
-   code execution;
-   document-processing actions;
-   web/provider search;
-   arbitrary external actions.

This is a deliberate V1 boundary, not a permanent retrieval-only
definition.

# 4. Architectural Position

The validated context and prompt path remains unchanged:

``` text
Planner
↓
ExecutionPlan
↓
Retriever Integration
↓
Retriever
↓
RetrievedContext
↓
Context Budgeting
↓
BudgetedContext
↓
Prompt Builder
↓
Prompt
```

Model Routing remains:

``` text
ExecutionPlan
↓
ModelRouter
↓
ModelRoute
```

Tool Routing is an independent parallel branch:

``` text
ExecutionPlan
↓
ToolRouter
↓
ToolRoute
```

Combined view:

``` text
                         ExecutionPlan
                              │
          ┌───────────────────┼────────────────────┐
          │                   │                    │
          ▼                   ▼                    ▼
Retriever path          ModelRouter           ToolRouter
          │                   │                    │
          ▼                   ▼                    ▼
       Prompt              ModelRoute            ToolRoute
```

Future Control Plane orchestration may coordinate `Prompt`,
`ModelRoute`, and `ToolRoute`.

Tool Routing is neither before nor after Model Routing. Neither routing
subsystem depends on the other.

# 5. Ownership

Tool Routing owns:

-   semantic information-access capability selection;
-   deterministic routing policy;
-   explicit no-capability routing;
-   `ToolRoute` construction;
-   deterministic routing explanation;
-   boundary validation;
-   output validation;
-   routing invariant validation.

Tool Routing does not own:

-   query analysis or semantic planning;
-   resource-requirement determination;
-   operation-intent inference;
-   retrieval;
-   context budgeting;
-   prompt construction;
-   model selection or execution;
-   tool discovery or registration;
-   MCP tool selection;
-   runtime capability resolution;
-   argument construction;
-   tool invocation;
-   execution ordering;
-   retries, fallback, timeout, cost, or latency policy;
-   result processing;
-   Control Plane orchestration.

Boundary:

``` text
Planner                         owns semantic planning and information requirements
Retriever                       owns information acquisition
Context Budgeting               owns context/token allocation
Prompt Builder                  owns prompt construction
Model Routing                   owns semantic model-capability selection
Tool Routing                    owns semantic information-access capability selection
Future Tool Execution Integration owns semantic capability → runtime binding
Future Control Plane            owns decision coordination and execution flow
MCP / Tool Infrastructure       owns exposure and concrete invocation
```

# 6. Canonical Input Contract

`ExecutionPlan` is the only Tool Router input contract in V1.

``` python
ToolRouter.route(execution_plan: ExecutionPlan) -> ToolRoute
```

The only V1 capability-selection authority is:

``` text
ExecutionPlan.resource_requirements
```

Boundary-valid context:

``` text
ExecutionPlan.version
ExecutionPlan.processing_goal
ExecutionPlan.resource_requirements
```

Non-authoritative fields:

``` text
ExecutionPlan.complexity
ExecutionPlan.processing_goal
ExecutionPlan.decision_trace
```

The Router must not accept raw query text, `PlanningContext`,
`RetrievedContext`, `BudgetedContext`, `Prompt`, `ModelRoute`, MCP
objects, callables, runtime tool lists, configuration, provider clients,
or infrastructure state.

# 7. ToolCapability

File: `routing/tool_capability.py`

``` python
@unique
class ToolCapability(Enum):
    KNOWLEDGE_ACCESS = "knowledge_access"
    MEMORY_ACCESS = "memory_access"
    SESSION_ACCESS = "session_access"
```

`KNOWLEDGE_ACCESS` means semantic access to persisted knowledge is
required.

`MEMORY_ACCESS` means semantic access to persistent user memory is
required.

`SESSION_ACCESS` means semantic access to session or conversation state
is required.

The enum must not encode MCP names, Python functions, module paths,
ChromaDB, providers, deployments, availability, cost, latency, execution
order, arguments, retries, or health state.

Invariants:

-   exactly three V1 members;
-   unique stable semantic values;
-   no behavior;
-   no infrastructure mapping;
-   membership changes require architecture review.

It is not a tool registry.

# 8. ToolRoute

File: `routing/tool_route.py`

``` python
@dataclass(frozen=True)
class ToolRoute:
    capabilities: tuple[ToolCapability, ...]
    reason: str
    version: int = CURRENT_SCHEMA_VERSION
```

`CURRENT_SCHEMA_VERSION = 1`.

No `tool_required` field: `bool(capabilities)` derives it.

No `tool_count` field: `len(capabilities)` derives it.

No concrete tool names, function identities, MCP names, arguments,
execution order, runtime state, `ExecutionPlan`, `ProcessingGoal`, or
`ResourceRequirements` may be stored.

Stable `to_dict()` key order:

``` text
capabilities
reason
version
```

Invariants:

-   immutable;
-   exactly `capabilities`, `reason`, `version`;
-   capabilities is a tuple;
-   every member is a valid `ToolCapability`;
-   no duplicates;
-   canonical ordering;
-   non-empty deterministic reason;
-   supported schema version;
-   empty tuple is valid and explicitly means no capability is required.

# 9. Canonical Capability Ordering

Exact order:

``` text
KNOWLEDGE_ACCESS
MEMORY_ACCESS
SESSION_ACCESS
```

This follows the stable `ResourceRequirements` order: knowledge, memory,
session.

The Router constructs canonical order directly. The Validator rejects
non-canonical order and never repairs it.

# 10. Deterministic Routing Policy

Exact mapping:

``` text
knowledge=True → KNOWLEDGE_ACCESS
memory=True    → MEMORY_ACCESS
session=True   → SESSION_ACCESS
```

Bidirectional invariants:

``` text
knowledge=True ↔ KNOWLEDGE_ACCESS present
memory=True    ↔ MEMORY_ACCESS present
session=True   ↔ SESSION_ACCESS present
```

All requirements false must produce `capabilities=()`.

There is no default, fallback, implicit `ProcessingGoal` capability,
complexity-based capability, or `DecisionTrace` capability.

# 11. Exhaustive Routing Matrix

  -----------------------------------------------------------------------------------------------------------
  Knowledge         Memory            Session           Capabilities
  ----------------- ----------------- ----------------- -----------------------------------------------------
  False             False             False             `()`

  False             False             True              `(SESSION_ACCESS,)`

  False             True              False             `(MEMORY_ACCESS,)`

  False             True              True              `(MEMORY_ACCESS, SESSION_ACCESS)`

  True              False             False             `(KNOWLEDGE_ACCESS,)`

  True              False             True              `(KNOWLEDGE_ACCESS, SESSION_ACCESS)`

  True              True              False             `(KNOWLEDGE_ACCESS, MEMORY_ACCESS)`

  True              True              True              `(KNOWLEDGE_ACCESS, MEMORY_ACCESS, SESSION_ACCESS)`
  -----------------------------------------------------------------------------------------------------------

Exact reasons:

``` text
()
→ "no resource access capabilities required"

(SESSION_ACCESS,)
→ "session requirement routes to session access capability"

(MEMORY_ACCESS,)
→ "memory requirement routes to memory access capability"

(MEMORY_ACCESS, SESSION_ACCESS)
→ "memory and session requirements route to memory and session access capabilities"

(KNOWLEDGE_ACCESS,)
→ "knowledge requirement routes to knowledge access capability"

(KNOWLEDGE_ACCESS, SESSION_ACCESS)
→ "knowledge and session requirements route to knowledge and session access capabilities"

(KNOWLEDGE_ACCESS, MEMORY_ACCESS)
→ "knowledge and memory requirements route to knowledge and memory access capabilities"

(KNOWLEDGE_ACCESS, MEMORY_ACCESS, SESSION_ACCESS)
→ "knowledge, memory, and session requirements route to knowledge, memory, and session access capabilities"
```

Implementation must use an explicit exhaustive policy mapping.
Unsupported state fails explicitly.

# 12. ProcessingGoal Policy

`processing_goal` must be valid at the routing boundary but does not
independently alter capability selection.

For `GENERAL`, `KNOWLEDGE`, `MEMORY`, `SESSION`, `DOCUMENT`, and `CODE`,
selection remains exclusively controlled by `resource_requirements`.

Example:

``` text
ProcessingGoal.MEMORY
resource_requirements.memory=False
```

does not add `MEMORY_ACCESS`.

Tool Routing does not repair or reinterpret Planner decisions.

# 13. Excluded Routing Signals

V1 must not route using raw or normalized query text, `DecisionTrace`,
`Complexity`, `ProcessingGoal` as an independent authority, retrieved
content, retrieval scores, budgeting metadata, prompt content, token
count, `ModelRoute`, MCP exposure, callable availability, runtime
availability, CPU/RAM/network state, latency history, quality history,
cost, environment variables, time, randomness, or mutable global state.

# 14. ToolRouter Lifecycle

File: `routing/tool_router.py`

``` text
receive ExecutionPlan
↓
validate input boundary
↓
read ResourceRequirements
↓
apply exact eight-state mapping
↓
construct ToolRoute
↓
validate output
↓
validate routing invariant
↓
return ToolRoute
```

The Router must not mutate input, parse query text or `DecisionTrace`,
call Retriever, Model Router, Prompt Builder, MCP, or infrastructure,
load configuration, discover tools, resolve bindings, execute tools,
retry, repair state, or return a default capability.

# 15. Validation

File: `routing/tool_routing_validator.py`

`ToolRoutingValidator` validates Tool Routing boundary assumptions only.

Input validation rejects:

-   non-`ExecutionPlan`;
-   unsupported `ExecutionPlan.version`;
-   invalid `ProcessingGoal`;
-   invalid `ResourceRequirements`;
-   non-boolean knowledge, memory, or session fields.

It does not validate Planner heuristics, complexity estimation, trace
wording, or Planner semantic consistency beyond frozen Planner
invariants.

Output validation rejects:

-   non-`ToolRoute`;
-   non-tuple capabilities;
-   invalid capability members;
-   duplicates;
-   non-canonical ordering;
-   non-string, empty, or whitespace reason;
-   unsupported `ToolRoute.version`.

Routing invariant validation enforces exact requirement-capability
equivalence, empty-route equivalence, and exact capability-to-reason
mapping.

Validation never repairs state.

# 16. Failure Behavior

Invalid state fails early and explicitly.

Forbidden:

-   default capability;
-   fallback capability;
-   silent omission or addition;
-   silent deduplication;
-   automatic sorting as repair;
-   query re-analysis;
-   Planner decision repair;
-   MCP or infrastructure fallback;
-   partial route return.

Tool Routing validation failures raise `ToolRoutingValidationError`.

# 17. Exception Ownership

Modify `routing/exceptions.py`.

Add exactly:

``` text
ToolRoutingError
└── ToolRoutingValidationError
```

Do not add tool-not-found, unavailable, execution, timeout, argument,
MCP, or capability-resolution exceptions. Those belong to future
integration/execution/infrastructure layers.

# 18. Dependency Direction

Allowed:

``` text
routing Tool Routing modules
↓
planner.execution_plan
planner.processing_goal
planner.resource_requirements
```

Internal Tool Routing modules may depend on Tool Routing domain modules.

Tool Routing and Model Routing may coexist in `routing/` but must not
depend on each other.

Forbidden Tool Routing dependencies:

``` text
mcp_server
memory
conversation_memory
services
retriever
integration
budgeting
prompt_builder
llm
config.settings
observability
ModelRouter
ModelRoute
```

Future Tool Execution Integration may depend on `ToolRoute` and
`ToolCapability`. Tool Routing never depends on runtime tool
infrastructure.

# 19. Package and File Architecture

Add:

``` text
routing/
├── tool_capability.py
├── tool_route.py
├── tool_router.py
└── tool_routing_validator.py
```

Modify:

``` text
routing/__init__.py
routing/exceptions.py
```

No other production file should be modified unless implementation review
proves a required defect.

Do not create registries, adapters, providers, executors, resolvers,
bindings, policy frameworks, metadata models, or descriptors.

Public exports:

``` text
ToolCapability
ToolRoute
ToolRouter
ToolRoutingError
ToolRoutingValidationError
```

`ToolRoutingValidator` remains internal.

# 20. Implementation Sequence

Implementation occurs only after explicit architecture freeze.

1.  Create `tool_capability.py` with the exact enum.
2.  Create immutable, versioned `tool_route.py` with stable
    serialization.
3.  Add exactly two Tool Routing exceptions without changing Model
    Routing exceptions.
4.  Create `tool_routing_validator.py` with input, output, and invariant
    validation.
5.  Create `tool_router.py` with the exact eight-state policy.
6.  Update `routing/__init__.py` with frozen public exports.
7.  Create and run Tool Routing subsystem tests.
8.  Run Planner-to-Tool-Router cross-layer tests.
9.  Run frozen upstream subsystem tests.
10. Run full regression; zero failures required.
11. Review every created and modified file against this architecture.
12. Only after acceptance update `CHANGELOG.md`, `Project_snapshot.md`,
    `AI_ECOSYSTEM_BOOTSTRAP.md`, and `AI_ECOSYSTEM_FILE_MANIFEST.json`.

# 21. Test Architecture

Create:

``` text
tests/routing/
├── test_tool_capability.py
├── test_tool_route.py
├── test_tool_routing_validator.py
├── test_tool_router.py
└── test_tool_router_pipeline.py
```

`test_tool_capability.py` validates exact membership, values, and
uniqueness.

`test_tool_route.py` validates construction, immutability, tuple
storage, empty tuple support, default version, stable serialization,
exact key order, and enum-value serialization.

`test_tool_routing_validator.py` validates all input/output rejection
branches and every routing invariant mismatch. Controlled frozen-object
corruption is allowed only where required to reach inaccessible
validator branches.

`test_tool_router.py` exhaustively validates `000` through `111`, exact
tuple, order, reason, output type, deterministic replay, and
non-mutation. It separately proves complexity, `ProcessingGoal`, and
`DecisionTrace` independence. Avoid unnecessary full combinatorial
explosion.

`test_tool_router_pipeline.py` validates:

``` text
QueryAnalyzer
↓
PlanningContext
↓
PlannerBuilder
↓
ExecutionPlan
↓
ToolRouter
↓
ToolRoute
```

Use representative no-resource, knowledge, memory, session, and
multi-resource Planner outputs. Verify real contract consumption,
non-mutation, exact mapping, and deterministic replay.

Do not include Retriever, Retriever Integration, Context Budgeting,
Prompt Builder, Model Router, or MCP.

# 22. Cross-Layer Test Boundaries

Required:

``` text
Planner → ExecutionPlan → ToolRouter → ToolRoute
```

Not Tool Routing cross-layer tests:

``` text
Retriever → ToolRouter
PromptBuilder → ToolRouter
ModelRouter → ToolRouter
MCP → ToolRouter
```

Future Tool Execution Integration owns `ToolRoute → runtime binding`
tests.

Future Control Plane orchestration owns coordination tests across
`Prompt`, `ModelRoute`, and `ToolRoute`.

# 23. Acceptance Criteria

Tool Routing V1 is complete only when:

-   frozen upstream contracts remain unchanged;
-   `ExecutionPlan` is the only input;
-   `resource_requirements` is the only selection authority;
-   `ToolCapability` has exactly three frozen members;
-   `ToolRoute` is immutable and versioned;
-   empty capabilities explicitly mean no capability required;
-   all eight states have exact deterministic routes;
-   canonical order and exact reasons are enforced;
-   `ProcessingGoal`, `Complexity`, and `DecisionTrace` do not alter
    selection;
-   raw query text is not accepted;
-   no MCP name or function identity enters routing contracts;
-   no discovery, runtime resolution, execution, infrastructure
    inspection, or configuration loading occurs;
-   Model Routing responsibility is not duplicated;
-   invariant validation exists;
-   invalid state fails explicitly;
-   inputs are not mutated;
-   stable serialization exists;
-   subsystem tests pass;
-   Planner-to-Tool-Router tests pass;
-   frozen upstream tests pass;
-   full regression has zero failures;
-   architecture and file-by-file implementation reviews pass.

# 24. Engineering Constitution Quality Gates

  -----------------------------------------------------------------------
  Gate                    Result                  Judgment
  ----------------------- ----------------------- -----------------------
  Mission Alignment       PASS                    Explicit capability
                                                  decisions support
                                                  avoiding unnecessary
                                                  execution.

  Single Responsibility   PASS                    Semantic
                                                  information-access
                                                  capability selection
                                                  only.

  Ownership Clarity       PASS                    Planning, selection,
                                                  binding, execution,
                                                  MCP, and orchestration
                                                  remain separate.

  Dependency Correctness  PASS                    Depends only on
                                                  required Planner domain
                                                  contracts.

  No Regret Rule          PASS                    Every public concept
                                                  has a stable V1
                                                  responsibility;
                                                  speculative
                                                  abstractions are
                                                  rejected.

  Observability           PASS                    Deterministic reason
                                                  provides decision
                                                  visibility without
                                                  inventing a new
                                                  subsystem.

  Testability             PASS                    Pure exhaustive
                                                  eight-state routing
                                                  authority.

  Stability               PASS                    Semantic capabilities
                                                  survive infrastructure
                                                  replacement.

  Simplicity              PASS                    Four focused modules
                                                  and two domain
                                                  exceptions.

  Future Evolution        PASS                    Action routing is
                                                  explicitly deferred
                                                  until semantic
                                                  authority exists.
  -----------------------------------------------------------------------

# 25. Scalability Analysis

V1 has `2³ = 8` routing states. An exhaustive mapping is safer than a
policy engine.

Future capability additions require architecture review answering:

1.  Which upstream contract owns the semantic requirement?
2.  Is the requirement deterministic?
3.  Can Tool Routing consume it without re-analysis?
4.  Is the capability stable across infrastructure replacement?
5.  Is a new public contract necessary?

This prevents `ToolCapability` from degrading into a tool registry.

No V1 abstraction is introduced solely for hypothetical scale.

# 26. Determinism and Non-Mutation

Identical valid `ExecutionPlan` input must produce the same capability
tuple, order, reason, and `ToolRoute`.

Routing cannot depend on time, randomness, network, MCP/provider/machine
state, environment variables, previous routes, mutable global state, or
unordered iteration.

The Router never modifies `ExecutionPlan`, `ProcessingGoal`,
`Complexity`, `ResourceRequirements`, or `DecisionTrace`.

`ToolRoute` is immutable.

# 27. Infrastructure Independence

Capabilities are semantic.

`KNOWLEDGE_ACCESS` remains valid if implemented by ChromaDB, PostgreSQL,
a local index, a remote service, MCP, or direct Python integration.

The same principle applies to memory and session access.

Current MCP exposure does not define Tool Routing architecture.

Legacy `search_knowledge()` must not become the canonical binding for
`KNOWLEDGE_ACCESS` because it is a composite path overlapping session,
memory, knowledge, budgeting, and formatting responsibilities.

Runtime binding belongs to future Tool Execution Integration.

# 28. Future Control Plane Integration

Future orchestration may coordinate:

``` text
ExecutionPlan
Prompt
ModelRoute
ToolRoute
```

Questions such as execution ordering, pre-inference capability
execution, prompt reconstruction after tool results, no-model execution,
model/tool coordination, and execution failure policy belong to future
Control Plane orchestration.

Tool Routing answers only:

``` text
Which currently supported semantic information-access capabilities are required by the Planner decision?
```

# 29. Rejected Alternatives

-   Raw-query routing: duplicates Planner analysis.
-   `DecisionTrace` parsing: turns diagnostic text into a hidden
    protocol.
-   Adding operation intent to `ExecutionPlan` for V1: redesigns frozen
    upstream architecture for a downstream subsystem.
-   `ProcessingGoal`-only routing: insufficient and conflicts with
    explicit resource requirements.
-   Universalizing `ResourceRequirements`: valid only for exact V1
    access-capability equivalence.
-   Direct MCP or Python function routing: infrastructure coupling.
-   Tool/capability registry: unjustified for three static capabilities.
-   Tool discovery: runtime integration concern.
-   Runtime resolution in Tool Router: mixes selection and binding.
-   Tool execution in Tool Router: violates decision/execution
    separation.
-   `ModelRoute` or `ModelRouter` dependency: false coupling.
-   Memory/session write routing in V1: missing operation-level semantic
    authority.
-   Legacy `search_knowledge()` as canonical capability: composite
    legacy orchestration.
-   Runtime-state routing: no operational policy layer currently owns
    such authority.

# 30. Architectural Invariants

> `ExecutionPlan` is the only Tool Router input in V1.

> `ExecutionPlan.resource_requirements` is the only V1
> capability-selection authority.

> Tool Routing selects semantic information-access capabilities, not
> concrete tools.

> `knowledge=True` exactly corresponds to `KNOWLEDGE_ACCESS`.

> `memory=True` exactly corresponds to `MEMORY_ACCESS`.

> `session=True` exactly corresponds to `SESSION_ACCESS`.

> Empty capabilities explicitly represent no required capability.

> `ProcessingGoal`, `Complexity`, and `DecisionTrace` do not alter V1
> selection.

> Tool Routing does not execute tools or resolve runtime bindings.

> Tool Routing does not inspect MCP or infrastructure state.

> Tool Routing and Model Routing are independent parallel branches.

> Tool Routing never mutates Planner contracts.

> Identical valid input produces identical `ToolRoute`.

> Action-oriented routing is deferred until operation-level semantic
> authority is established.

```text
# 31. Architecture and Implementation Review Result

``` text
PASS — TOOL ROUTING V1 ACCEPTED AND ARCHITECTURALLY FROZEN