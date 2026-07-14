# Model Routing V1 Architecture

Version: 1.0\
Status: Architecture Frozen\
Scope: Model Routing Subsystem\
Target Release: AI Ecosystem V0.6.0

------------------------------------------------------------------------

# 1. Purpose

Model Routing is a deterministic Control Plane subsystem. Its sole
responsibility is to select the semantic model capability target
required by a Planner decision.

Canonical transformation:

``` text
ExecutionPlan
↓
ModelRouter
↓
ModelRoute
```

The Router does not execute models, resolve providers, inspect prompts,
perform retrieval, budget context, or construct prompts.

# 2. Architectural Position

The validated upstream path remains:

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

Model Routing is a parallel branch from `ExecutionPlan`:

``` text
ExecutionPlan
↓
ModelRouter
↓
ModelRoute
```

Future execution joins:

``` text
Prompt + ModelRoute
↓
Future Model Execution
```

Model Routing must not be inserted after Prompt Builder as a
prompt-inspection stage.

# 3. Input Contract

`ExecutionPlan` is the only Model Router input contract in V1.

Public API:

``` python
ModelRouter.route(execution_plan: ExecutionPlan) -> ModelRoute
```

The Router must not accept raw query text, `Prompt`, `BudgetedContext`,
`RetrievedContext`, metadata, infrastructure configuration, provider
clients, or model executors.

Planner owns query interpretation, goal classification, and complexity
estimation. Re-analysis inside routing would duplicate Planner
responsibility and create conflicting authorities.

# 4. Ownership

Model Routing owns:

-   semantic model-target selection
-   deterministic routing policy
-   route construction
-   deterministic routing explanation
-   routing boundary validation
-   routing output and invariant validation

Model Routing does not own:

-   query analysis or complexity estimation
-   retrieval
-   context budgeting
-   prompt construction
-   provider selection
-   concrete model resolution
-   model loading or inference
-   tool routing
-   retry, fallback, timeout, cost, or latency policy

Boundary:

``` text
Planner                         owns semantic planning
Retriever                       owns information acquisition
Context Budgeting               owns context/token allocation
Prompt Builder                  owns prompt construction
Model Routing                   owns semantic model-target selection
Future Model Execution          owns runtime resolution/orchestration
Model Infrastructure            owns invocation
```

# 5. ModelTarget

File: `routing/model_target.py`

``` python
@unique
class ModelTarget(Enum):
    LIGHTWEIGHT = "lightweight"
    STANDARD = "standard"
    ADVANCED = "advanced"
```

Meanings:

-   `LIGHTWEIGHT`: low expected inference effort.
-   `STANDARD`: normal expected reasoning effort.
-   `ADVANCED`: significant expected reasoning effort.

`ModelTarget` is a semantic capability class. It must not encode
provider, deployment, model family, local/cloud placement, cost, speed,
availability, context window, or quantization.

Concrete names such as `qwen3:4b`, Claude, GPT, Ollama, or OpenAI are
forbidden as routing targets.

Invariants:

-   target is exactly one defined enum member
-   values are stable semantic identifiers
-   enum contains no routing behavior
-   enum contains no infrastructure mapping
-   membership changes require architecture review

# 6. ModelRoute

File: `routing/model_route.py`

Canonical immutable output:

``` python
@dataclass(frozen=True)
class ModelRoute:
    target: ModelTarget
    reason: str
    version: int = CURRENT_SCHEMA_VERSION
```

`CURRENT_SCHEMA_VERSION = 1`.

Fields:

-   `target`: selected semantic capability target
-   `reason`: deterministic human-readable routing explanation
-   `version`: ModelRoute schema version

Stable `to_dict()` key order:

``` text
target
reason
version
```

Example:

``` json
{
  "target": "advanced",
  "reason": "high complexity routes to advanced target",
  "version": 1
}
```

Invariants:

-   immutable
-   exactly `target`, `reason`, `version`
-   valid `ModelTarget`
-   non-empty string reason
-   deterministic reason
-   supported schema version
-   no ExecutionPlan, Prompt, infrastructure configuration, or runtime
    model identity

# 7. Routing Authority and Policy

V1 target-selection authority is only:

``` text
ExecutionPlan.complexity
```

Exact exhaustive mapping:

``` text
Complexity.LOW
→ ModelTarget.LIGHTWEIGHT

Complexity.MEDIUM
→ ModelTarget.STANDARD

Complexity.HIGH
→ ModelTarget.ADVANCED
```

There is no default route and no fallback route. Unsupported routing
state fails explicitly.

# 8. ProcessingGoal Policy

`ExecutionPlan.processing_goal` must be valid at the routing boundary,
but it does not modify the V1 target.

For every current goal:

``` text
GENERAL
KNOWLEDGE
MEMORY
SESSION
DOCUMENT
CODE
```

the mapping remains:

``` text
LOW    → LIGHTWEIGHT
MEDIUM → STANDARD
HIGH   → ADVANCED
```

No hidden goal-specific minimums are permitted. Goal-specific routing
requires measured evidence and architecture review.

# 9. Excluded Routing Signals

V1 must not route using:

-   ResourceRequirements
-   DecisionTrace text
-   Prompt content
-   raw query text
-   retrieved context or retrieval scores
-   retrieval or budgeting metadata
-   prompt token count
-   CPU or RAM state
-   model/provider availability
-   latency history
-   quality history
-   cost
-   environment variables
-   time
-   randomness

`ResourceRequirements` describes information acquisition, not model
capability. `DecisionTrace` is diagnostic text. Prompt inspection would
duplicate Planner analysis. Runtime signals belong to future execution
policy.

# 10. ModelRouter

File: `routing/model_router.py`

Public API:

``` python
ModelRouter.route(execution_plan: ExecutionPlan) -> ModelRoute
```

Lifecycle:

``` text
receive ExecutionPlan
↓
validate input
↓
read complexity
↓
apply explicit deterministic mapping
↓
construct ModelRoute
↓
validate output and routing invariant
↓
return ModelRoute
```

Exact V1 reason strings:

``` text
LOW    → "low complexity routes to lightweight target"
MEDIUM → "medium complexity routes to standard target"
HIGH   → "high complexity routes to advanced target"
```

The Router must not mutate input, call infrastructure, load
configuration, inspect prompt content, retry, silently repair invalid
state, or return a default target.

# 11. Validation

File: `routing/model_routing_validator.py`

The routing subsystem validates only assumptions required at its own
boundary. It does not replace Planner validation.

Input validation rejects:

-   non-ExecutionPlan input
-   unsupported ExecutionPlan version
-   invalid ExecutionPlan complexity
-   invalid ExecutionPlan processing goal

Do not duplicate Planner semantic validation. Do not validate query
classification rules, Planner heuristics, ResourceRequirements semantic
consistency, or DecisionTrace explanation correctness.

Output validation rejects:

-   non-ModelRoute output
-   invalid ModelTarget
-   non-string reason
-   empty or whitespace-only reason
-   unsupported ModelRoute version

Routing invariant validation enforces:

``` text
LOW    ↔ LIGHTWEIGHT
MEDIUM ↔ STANDARD
HIGH   ↔ ADVANCED
```

A route inconsistent with the input complexity is invalid. Invalid state
fails explicitly and is never repaired.

# 12. Exceptions

File: `routing/exceptions.py`

Introduce exactly:

``` text
ModelRoutingError
ModelRoutingValidationError
```

Hierarchy:

``` text
ModelRoutingError
↓
ModelRoutingValidationError
```

Do not introduce model-not-found, provider-unavailable, timeout,
fallback, execution, or load exceptions. Those belong to future runtime
integration/infrastructure.

# 13. Package Architecture

Use the existing top-level `routing/` package:

``` text
routing/
├── __init__.py
├── exceptions.py
├── model_target.py
├── model_route.py
├── model_router.py
└── model_routing_validator.py
```

Public API from `routing/__init__.py` exposes exactly:

-   ModelTarget
-   ModelRoute
-   ModelRouter
-   ModelRoutingError
-   ModelRoutingValidationError

`ModelRoutingValidator` remains internal.

No additional production files are required for V1.

# 14. Dependency Direction

Allowed production dependencies:

``` text
routing
↓
planner.execution_plan

routing
↓
planner.complexity

routing
↓
planner.processing_goal
```

Internal routing modules may depend on routing modules.

Forbidden production dependencies:

-   prompt_builder
-   budgeting
-   retriever
-   integration
-   services
-   llm
-   ollama
-   openai
-   config.settings
-   observability
-   mcp_server
-   conversation_memory
-   memory

The Router must not import `CHAT_MODEL`, `SUMMARY_MODEL`,
`OllamaGenerator`, `Prompt`, `BudgetedContext`, or `RetrievedContext`.

Infrastructure must depend on routing contracts; routing must never
depend on model infrastructure.

# 15. Infrastructure Boundary

The legacy runtime's direct `CHAT_MODEL` and `OllamaGenerator` use does
not define Model Routing architecture.

`CHAT_MODEL` is not a routing target.

`SUMMARY_MODEL` must not be reused as the lightweight routed chat model
because summarization and routed query execution are different
responsibilities.

Future Model Execution Integration will resolve:

``` text
ModelTarget.LIGHTWEIGHT → configured runtime binding
ModelTarget.STANDARD    → configured runtime binding
ModelTarget.ADVANCED    → configured runtime binding
```

Concrete bindings are outside Model Routing V1.

# 16. Determinism and Non-Mutation

Identical valid `ExecutionPlan` input must produce identical
`ModelRoute`.

Routing must not depend on time, randomness, network state, provider
state, machine state, environment variables, previous routes, mutable
global state, or unordered iteration.

The Router must not modify `ExecutionPlan`, `Complexity`,
`ProcessingGoal`, `ResourceRequirements`, or `DecisionTrace`.

`ModelRoute` is immutable.

# 17. Test Architecture

Create:

``` text
tests/routing/
├── test_model_target.py
├── test_model_route.py
├── test_model_routing_validator.py
├── test_model_router.py
└── test_model_router_pipeline.py
```

`test_model_target.py` validates exact membership, exact enum values,
and uniqueness.

`test_model_route.py` validates construction, immutability, default
schema version, stable serialization, exact key order, and enum-value
serialization.

`test_model_routing_validator.py` validates input/output boundaries,
unsupported versions, deliberately corrupted
complexity/goal/target/reason branches, and complexity-target mismatch.
Controlled frozen-object corruption is allowed only in validator tests
to reach otherwise inaccessible branches.

`test_model_router.py` validates exact LOW/MEDIUM/HIGH mapping, exact
reason strings, deterministic replay, non-mutation, output type,
unsupported input rejection, no default route, and the complete
`6 ProcessingGoal × 3 Complexity = 18` matrix proving V1 is
complexity-only.

`test_model_router_pipeline.py` validates the real branch:

``` text
QueryAnalyzer
↓
PlanningContext
↓
PlannerBuilder
↓
ExecutionPlan
↓
ModelRouter
↓
ModelRoute
```

Use representative Planner outputs for LOW, MEDIUM, and HIGH complexity.
Verify Planner output non-mutation, valid route, mapping correctness,
and deterministic replay.

Do not include Retriever, Retriever Integration, Context Budgeting, or
Prompt Builder in routing pipeline tests. Doing so would encode a false
sequential dependency.

# 18. Acceptance Criteria

Model Routing V1 is complete only when:

-   ExecutionPlan is the only Router input
-   ModelRoute is the canonical immutable output
-   ModelTarget contains exactly LIGHTWEIGHT, STANDARD, ADVANCED
-   LOW → LIGHTWEIGHT
-   MEDIUM → STANDARD
-   HIGH → ADVANCED
-   all current ProcessingGoal values preserve complexity-only mapping
-   no prompt inspection or raw query analysis occurs
-   no provider or concrete model name exists in routing output
-   no runtime model resolution or inference occurs
-   no configuration or infrastructure dependency exists
-   routing and reason strings are deterministic
-   inputs are not mutated
-   invalid state fails explicitly
-   routing invariant validation exists
-   stable serialization exists
-   routing subsystem tests pass
-   Planner-to-Router cross-layer tests pass
-   frozen upstream subsystem tests pass
-   full project regression passes with zero failures
-   architecture review and file-by-file implementation review pass

# 19. Explicitly Deferred Beyond V1

Deferred:

-   concrete model-name selection
-   provider selection
-   local/cloud selection
-   provider/model availability checks
-   dynamic fallback
-   retry and timeout policy
-   cost-aware routing
-   latency-aware routing
-   quality-history routing
-   adaptive or learned routing
-   ensembles
-   model capability registries
-   plugin systems
-   routing configuration frameworks
-   target-to-model binding
-   model execution
-   tool routing

Future capabilities must extend around the V1 contracts and must not
silently redefine Model Routing ownership.

# 20. Architectural Invariants

> ExecutionPlan is the only Model Router input contract in V1.

> ExecutionPlan.complexity is the only target-selection authority in V1.

> ProcessingGoal is boundary-valid semantic context but does not alter
> the V1 target.

> Model Routing selects semantic capability targets, not infrastructure
> identities.

> LOW routes to LIGHTWEIGHT.

> MEDIUM routes to STANDARD.

> HIGH routes to ADVANCED.

> ModelRoute is the canonical immutable routing output.

> Prompt content is never inspected by Model Routing.

> Model Routing performs no model resolution and no inference.

> Model Routing has no infrastructure or configuration dependency.

> Identical valid inputs produce identical routes.

> Invalid routing state fails explicitly.

> Model Routing never mutates Planner contracts.

# 21. Status

Architecture Status:

``` text
FROZEN FOR V1
```

Implementation Status:

``` text
NOT YET VALIDATED
```

Validated upstream baseline before implementation:

``` text
313 passed
0 failures
1 external ChromaDB deprecation warning
```

Frozen upstream subsystems that must not be redesigned:

-   Planner V1
-   Retriever V1
-   Retriever Integration V1
-   Context Budgeting V1
-   Prompt Builder V1
