"""
Tests for platform/foundation/lifecycle.py

Verifies LifecycleState transitions and LifecycleManager callback orchestration.
"""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[3])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

from platcore.foundation.lifecycle import LifecycleManager, LifecycleState
from platcore.foundation.exceptions import InvalidLifecycleStateError


class TestLifecycleState:
    """Verify LifecycleState enum and transition rules."""

    def test_initial_state_is_created(self):
        assert LifecycleState.CREATED.value == 1  # auto() starts at 1

    def test_can_transition_to_valid(self):
        assert (
            LifecycleState.CREATED.can_transition_to(LifecycleState.INITIALIZING)
            is True
        )

    def test_cannot_transition_to_invalid(self):
        assert LifecycleState.CREATED.can_transition_to(LifecycleState.STARTED) is False

    def test_cannot_transition_backwards(self):
        assert (
            LifecycleState.INITIALIZED.can_transition_to(LifecycleState.CREATED)
            is False
        )

    def test_stopped_cannot_transition(self):
        assert LifecycleState.STOPPED.can_transition_to(LifecycleState.CREATED) is False
        assert LifecycleState.STOPPED.can_transition_to(LifecycleState.STARTED) is False

    def test_failed_cannot_transition(self):
        assert LifecycleState.FAILED.can_transition_to(LifecycleState.CREATED) is False
        assert LifecycleState.FAILED.can_transition_to(LifecycleState.STARTED) is False


class TestLifecycleManager:
    """Verify LifecycleManager state management."""

    def setup_method(self):
        self.manager = LifecycleManager()

    def test_default_state_is_created(self):
        assert self.manager.state == LifecycleState.CREATED

    def test_single_transition(self):
        self.manager.transition_to(LifecycleState.INITIALIZING)
        assert self.manager.state == LifecycleState.INITIALIZING

    def test_full_transition_sequence(self):
        self.manager.transition_to(LifecycleState.INITIALIZING)
        self.manager.transition_to(LifecycleState.INITIALIZED)
        self.manager.transition_to(LifecycleState.STARTING)
        self.manager.transition_to(LifecycleState.STARTED)
        self.manager.transition_to(LifecycleState.STOPPING)
        self.manager.transition_to(LifecycleState.STOPPED)
        assert self.manager.state == LifecycleState.STOPPED

    def test_invalid_transition_raises_error(self):
        with pytest.raises(InvalidLifecycleStateError, match="Cannot transition"):
            self.manager.transition_to(LifecycleState.STARTED)  # Skip INITIALIZING

    def test_invalid_transition_from_started(self):
        self.manager.transition_to(LifecycleState.INITIALIZING)
        self.manager.transition_to(LifecycleState.INITIALIZED)
        self.manager.transition_to(LifecycleState.STARTING)
        self.manager.transition_to(LifecycleState.STARTED)
        with pytest.raises(InvalidLifecycleStateError, match="Cannot transition"):
            self.manager.transition_to(LifecycleState.INITIALIZED)  # Backwards

    def test_transition_to_failed(self):
        self.manager.transition_to(LifecycleState.INITIALIZING)
        self.manager.transition_to(LifecycleState.FAILED)
        assert self.manager.state == LifecycleState.FAILED

    def test_failed_is_terminal(self):
        self.manager.transition_to(LifecycleState.INITIALIZING)
        self.manager.transition_to(LifecycleState.FAILED)
        with pytest.raises(InvalidLifecycleStateError):
            self.manager.transition_to(LifecycleState.STOPPED)


class TestLifecycleManagerCallbacks:
    """Verify lifecycle callback registration and invocation."""

    def setup_method(self):
        self.manager = LifecycleManager()
        self.callback_log = []

    def _record_callback(self, state):
        self.callback_log.append(state)

    def test_callback_invoked_on_transition(self):
        self.manager.register_callback(
            LifecycleState.INITIALIZING, self._record_callback
        )
        self.manager.transition_to(LifecycleState.INITIALIZING)
        assert self.callback_log == [LifecycleState.INITIALIZING]

    def test_callback_not_invoked_for_other_states(self):
        self.manager.register_callback(LifecycleState.STARTED, self._record_callback)
        self.manager.transition_to(LifecycleState.INITIALIZING)
        self.manager.transition_to(LifecycleState.INITIALIZED)
        self.manager.transition_to(LifecycleState.STARTING)
        assert self.callback_log == []  # Not yet STARTED
        self.manager.transition_to(LifecycleState.STARTED)
        assert self.callback_log == [LifecycleState.STARTED]

    def test_multiple_callbacks_for_same_state(self):
        log1 = []
        log2 = []

        def cb1(s):
            log1.append(s)

        def cb2(s):
            log2.append(s)

        self.manager.register_callback(LifecycleState.STARTED, cb1)
        self.manager.register_callback(LifecycleState.STARTED, cb2)
        self._start_full()
        assert log1 == [LifecycleState.STARTED]
        assert log2 == [LifecycleState.STARTED]

    def test_callbacks_fail_transitions_to_failed(self):
        def failing_callback(state):
            raise ValueError("callback failure")

        self.manager.register_callback(LifecycleState.INITIALIZING, failing_callback)
        with pytest.raises(
            InvalidLifecycleStateError, match="Lifecycle callback failed"
        ):
            self.manager.transition_to(LifecycleState.INITIALIZING)
        assert self.manager.state == LifecycleState.FAILED

    def test_register_non_callable_raises(self):
        with pytest.raises(ValueError, match="Callback must be callable"):
            self.manager.register_callback(LifecycleState.STARTED, "not_callable")  # type: ignore

    def _start_full(self):
        self.manager.transition_to(LifecycleState.INITIALIZING)
        self.manager.transition_to(LifecycleState.INITIALIZED)
        self.manager.transition_to(LifecycleState.STARTING)
        self.manager.transition_to(LifecycleState.STARTED)


class TestLifecycleManagerConvenience:
    """Verify convenience start/stop methods."""

    def setup_method(self):
        self.manager = LifecycleManager()

    def test_start_sequence(self):
        self.manager.start()
        assert self.manager.state == LifecycleState.STARTED

    def test_start_to_stop(self):
        self.manager.start()
        self.manager.stop()
        assert self.manager.state == LifecycleState.STOPPED

    def test_start_triggers_callbacks(self):
        log = []

        def cb(s):
            log.append(s)

        self.manager.register_callback(LifecycleState.INITIALIZING, cb)
        self.manager.register_callback(LifecycleState.INITIALIZED, cb)
        self.manager.register_callback(LifecycleState.STARTING, cb)
        self.manager.register_callback(LifecycleState.STARTED, cb)
        self.manager.start()
        assert log == [
            LifecycleState.INITIALIZING,
            LifecycleState.INITIALIZED,
            LifecycleState.STARTING,
            LifecycleState.STARTED,
        ]

    def test_stop_triggers_callbacks(self):
        log = []

        def cb(s):
            log.append(s)

        self.manager.register_callback(LifecycleState.STOPPING, cb)
        self.manager.register_callback(LifecycleState.STOPPED, cb)
        self.manager.start()
        self.manager.stop()
        assert log == [LifecycleState.STOPPING, LifecycleState.STOPPED]

    def test_start_from_non_created_raises(self):
        self.manager.transition_to(LifecycleState.INITIALIZING)
        with pytest.raises(InvalidLifecycleStateError):
            self.manager.start()

    def test_stop_from_non_started_raises(self):
        with pytest.raises(InvalidLifecycleStateError):
            self.manager.stop()


class TestLifecycleManagerThreadSafety:
    """Basic thread safety verification."""

    def test_concurrent_state_reads(self):
        import threading

        manager = LifecycleManager()
        errors = []

        def read_state():
            try:
                for _ in range(100):
                    _ = manager.state
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=read_state) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0
