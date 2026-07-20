"""
platform/foundation/lifecycle.py

Lifecycle management abstraction.

Provides a LifecycleManager that manages platform lifecycle state transitions
and allows components to register lifecycle callbacks. The manager does NOT
own service startup/shutdown logic — components register callbacks that are
invoked at the appropriate lifecycle phase.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from enum import Enum, auto
from typing import Final, Protocol

from .exceptions import InvalidLifecycleStateError


class LifecycleState(Enum):
    """
    Enumeration of platform lifecycle states.

    Purpose:
        Defines the valid states in the platform lifecycle state machine.
        Progression is monotonic: states transition forward and cannot
        return to a previous state except through a FAILED state.

    Values:
        CREATED: The manager has been instantiated.
        INITIALIZING: Lifecycle initialization has begun.
        INITIALIZED: Lifecycle initialization completed successfully.
        STARTING: Platform startup sequence is in progress.
        STARTED: Platform is fully started and operational.
        STOPPING: Platform shutdown sequence is in progress.
        STOPPED: Platform has been cleanly stopped.
        FAILED: An unrecoverable error occurred during any phase.
    """

    CREATED = auto()
    INITIALIZING = auto()
    INITIALIZED = auto()
    STARTING = auto()
    STARTED = auto()
    STOPPING = auto()
    STOPPED = auto()
    FAILED = auto()

    def can_transition_to(self, target: LifecycleState) -> bool:
        """
        Check whether a transition from this state to the target is valid.

        Args:
            target: The target lifecycle state.

        Returns:
            ``True`` if the transition is allowed, ``False`` otherwise.
        """
        return target in _TRANSITIONS.get(self, set())


# Define allowed transitions for lifecycle state machine
# Defined after LifecycleState to avoid NameError
_TRANSITIONS: dict[LifecycleState, set[LifecycleState]] = {
    LifecycleState.CREATED: {LifecycleState.INITIALIZING},
    LifecycleState.INITIALIZING: {LifecycleState.INITIALIZED, LifecycleState.FAILED},
    LifecycleState.INITIALIZED: {LifecycleState.STARTING},
    LifecycleState.STARTING: {LifecycleState.STARTED, LifecycleState.FAILED},
    LifecycleState.STARTED: {LifecycleState.STOPPING},
    LifecycleState.STOPPING: {LifecycleState.STOPPED, LifecycleState.FAILED},
    LifecycleState.STOPPED: set(),
    LifecycleState.FAILED: set(),
}


class LifecycleCallback(Protocol):
    """
    Protocol for lifecycle callbacks.

    A lifecycle callback is an asynchronous-compatible callable that
    performs work during a lifecycle phase transition.
    """

    def __call__(self, state: LifecycleState) -> None:
        ...


class LifecycleManager:
    """
    Platform lifecycle manager.

    Responsibility:
        Manage the deterministic lifecycle state machine for the platform.
        Components register lifecycle callbacks that are invoked when the
        corresponding state is entered.

    The manager does **not** own service startup or shutdown logic.
    Components are responsible for registering their own lifecycle
    callbacks. The manager only orchestrates the sequence of callbacks.

    Thread safety:
        State transitions are protected by a reentrant lock. Multiple
        threads may safely query the current state, but only one thread
        may perform transitions at a time.

    This is a stable public contract.
    """

    def __init__(self, initial_state: LifecycleState = LifecycleState.CREATED) -> None:
        """
        Initialize the lifecycle manager.

        Args:
            initial_state: The initial lifecycle state. Defaults to CREATED.
        """
        self._state: LifecycleState = initial_state
        self._lock: Final = threading.RLock()

        # Callback storage: maps LifecycleState to list of callbacks
        self._callbacks: dict[LifecycleState, list[LifecycleCallback]] = {}
        for state in LifecycleState:
            self._callbacks[state] = []

    @property
    def state(self) -> LifecycleState:
        """Return the current lifecycle state."""
        with self._lock:
            return self._state

    def register_callback(self, state: LifecycleState, callback: LifecycleCallback) -> None:
        """
        Register a callback to be invoked when the given state is entered.

        Args:
            state: The lifecycle state at which the callback should be invoked.
            callback: A callable accepting the current ``LifecycleState``.

        Raises:
            ValueError: If the callback is not callable.
        """
        if not callable(callback):
            raise ValueError("Callback must be callable")

        with self._lock:
            self._callbacks[state].append(callback)

    def transition_to(self, target: LifecycleState) -> None:
        """
        Transition to the target lifecycle state.

        This method:
            1. Validates that the transition is allowed.
            2. Updates the current state.
            3. Invokes all registered callbacks for the target state.
            4. If a callback raises an exception, transitions to FAILED.

        Args:
            target: The target lifecycle state.

        Raises:
            InvalidLifecycleStateError: If the transition is not allowed.
        """
        with self._lock:
            if not self._state.can_transition_to(target):
                raise InvalidLifecycleStateError(
                    f"Cannot transition from {self._state} to {target}"
                )

            self._state = target
            self._invoke_callbacks(target)

    def start(self) -> None:
        """
        Convenience method to start the platform lifecycle.

        Executes the full startup sequence: INITIALIZING -> INITIALIZED ->
        STARTING -> STARTED.

        Raises:
            InvalidLifecycleStateError: If the current state is not CREATED.
        """
        self.transition_to(LifecycleState.INITIALIZING)
        self.transition_to(LifecycleState.INITIALIZED)
        self.transition_to(LifecycleState.STARTING)
        self.transition_to(LifecycleState.STARTED)

    def stop(self) -> None:
        """
        Convenience method to stop the platform lifecycle.

        Executes the shutdown sequence: STOPPING -> STOPPED.

        Raises:
            InvalidLifecycleStateError: If the current state is not STARTED.
        """
        self.transition_to(LifecycleState.STOPPING)
        self.transition_to(LifecycleState.STOPPED)

    def _invoke_callbacks(self, state: LifecycleState) -> None:
        """
        Invoke all callbacks registered for the given state.

        Args:
            state: The lifecycle state whose callbacks to invoke.

        Raises:
            InvalidLifecycleStateError: Wraps any exception raised by a
                callback, transitioning to FAILED state.
        """
        for callback in self._callbacks.get(state, []):
            try:
                callback(state)
            except Exception as exc:
                self._state = LifecycleState.FAILED
                raise InvalidLifecycleStateError(
                    f"Lifecycle callback failed at state {state}: {exc}"
                ) from exc

