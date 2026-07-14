from __future__ import annotations

from enum import Enum, auto
from typing import Any, Optional, Tuple

from .participation import ParticipationCoordinator
from .result import ControlPlaneResult, ResultComposer
from model_execution.model_response import ModelResponse
from tool_execution.tool_execution_result import ToolExecutionResult


class LifecycleState(Enum):
    EXECUTION_REQUESTED = auto()
    EXECUTION_COORDINATING = auto()
    SUBSYSTEM_PARTICIPATION = auto()
    INDEPENDENT_BRANCH_PARTICIPATION = auto()
    EXECUTION_COMPLETING = auto()
    EXECUTION_COMPLETED = auto()


class LifecycleCoordinator:
    """Lifecycle Coordinator component.

    Responsibility:
        Own the deterministic Control Plane lifecycle for exactly one
        execution. This component enforces monotonic, deterministic state
        progression and delegates participation coordination and result
        composition to the corresponding components.

    Implementation note: This component does not implement retries,
    fallbacks, provider selection, or any execution policy.
    """

    def __init__(self, participation_coordinator: ParticipationCoordinator) -> None:
        self._participation = participation_coordinator
        self._result_composer = ResultComposer()
        self._state = LifecycleState.EXECUTION_REQUESTED

    @property
    def state(self) -> LifecycleState:
        return self._state

    def run(
        self,
        query: str,
        session_id: Optional[str],
        total_budget: int,
        reserved_budget: int,
        category_caps: Optional[dict],
        generator: Any | None,
    ) -> ControlPlaneResult:
        """Run one Control Plane execution lifecycle and return the
        immutable ControlPlaneResult.

        The lifecycle is deterministic and monotonic; each state is entered at
        most once and the lifecycle terminates in EXECUTION_COMPLETED with a
        composed ControlPlaneResult.
        """

        # 1. Execution Requested -> Execution Coordinating
        self._enter_state(LifecycleState.EXECUTION_COORDINATING)

        # 2. Coordinate participation (delegated)
        self._enter_state(LifecycleState.SUBSYSTEM_PARTICIPATION)

        # ParticipationCoordinator may internally manage independent branches.
        self._enter_state(LifecycleState.INDEPENDENT_BRANCH_PARTICIPATION)
        model_response, tool_result = self._participation.coordinate(
            query=query,
            session_id=session_id,
            total_budget=total_budget,
            reserved_budget=reserved_budget,
            category_caps=category_caps,
            generator=generator,
        )

        # 3. Execution Completing
        self._enter_state(LifecycleState.EXECUTION_COMPLETING)

        # Deterministic composition of completed branch outputs
        control_plane_result = self._result_composer.compose(model_response, tool_result)

        # 4. Execution Completed
        self._enter_state(LifecycleState.EXECUTION_COMPLETED)

        return control_plane_result

    def _enter_state(self, new_state: LifecycleState) -> None:
        # Ensure monotonic progression: cannot return to a previous state
        if new_state.value <= self._state.value:
            # Allow entering the first coordinating state when starting
            if not (self._state == LifecycleState.EXECUTION_REQUESTED and new_state == LifecycleState.EXECUTION_COORDINATING):
                raise RuntimeError(f"Invalid lifecycle transition from {self._state} to {new_state}")
        self._state = new_state
