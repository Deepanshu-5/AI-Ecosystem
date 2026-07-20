"""
Thread-safety tests for platform/foundation components.

Verifies that concurrent access to all foundation components is safe
and does not corrupt internal state.
"""

import sys
import threading
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[3])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

from platcore.foundation.lifecycle import LifecycleManager, LifecycleState
from platcore.foundation.clock import FrozenClock, SystemClock
from platcore.foundation.id_generator import UuidGenerator
from platcore.foundation.feature_flags import InMemoryFeatureFlagProvider
from platcore.foundation.service_registry import ServiceRegistry
from platcore.foundation.resource_registry import ResourceRegistry
from platcore.foundation.container import ServiceContainer


class TestLifecycleManagerThreadSafety:
    """Concurrent state transitions and reads."""

    def test_concurrent_transitions_and_reads(self):
        manager = LifecycleManager()
        errors = []

        def transition():
            try:
                manager.transition_to(LifecycleState.INITIALIZING)
                manager.transition_to(LifecycleState.INITIALIZED)
                manager.transition_to(LifecycleState.STARTING)
                manager.transition_to(LifecycleState.STARTED)
            except Exception as e:
                errors.append(e)

        def read():
            try:
                for _ in range(100):
                    _ = manager.state
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=transition)]
        threads += [threading.Thread(target=read) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestContainerThreadSafety:
    """Concurrent service registration and resolution."""

    def test_concurrent_register_and_resolve(self):
        container = ServiceContainer()
        errors = []

        # Pre-register base services
        container.register(SystemClock)
        container.register(UuidGenerator)

        def register_service():
            try:
                container.register(object, override=True)
            except Exception as e:
                errors.append(e)

        def resolve_service():
            try:
                for _ in range(50):
                    _ = container.resolve(SystemClock)
                    _ = container.resolve(UuidGenerator)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=resolve_service) for _ in range(5)]
        threads += [threading.Thread(target=register_service)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestRegistryThreadSafety:
    """Concurrent registry operations."""

    def test_concurrent_service_registry(self):
        registry = ServiceRegistry()
        errors = []

        def register_services():
            for i in range(100):
                try:
                    registry.register(f"svc_{i}", str)
                except Exception:
                    pass  # May collide with others, that's expected

        def read_services():
            for _ in range(50):
                try:
                    _ = registry.count
                    _ = registry.get_all()
                except Exception as e:
                    errors.append(e)

        threads = [threading.Thread(target=register_services) for _ in range(5)]
        threads += [threading.Thread(target=read_services) for _ in range(3)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert registry.count > 0

    def test_concurrent_resource_registry(self):
        registry = ResourceRegistry()
        errors = []

        from platcore.foundation.resource_registry import ResourceType

        def register_resources():
            for i in range(100):
                try:
                    registry.register(f"res_{i}", ResourceType.OTHER)
                except Exception:
                    pass

        threads = [threading.Thread(target=register_resources) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert registry.count > 0


class TestFeatureFlagThreadSafety:
    """Concurrent feature flag operations."""

    def test_concurrent_set_and_read(self):
        provider = InMemoryFeatureFlagProvider()
        errors = []

        def set_flags():
            for i in range(200):
                provider.set_flag(f"flag_{i}", i)
                provider.remove_flag(f"flag_{i}")
                provider.set_flag(f"flag_{i}", True)

        def read_flags():
            for i in range(200):
                try:
                    provider.is_enabled(f"flag_{i}")
                    provider.get_value(f"flag_{i}")
                except Exception as e:
                    errors.append(e)

        threads = [
            threading.Thread(target=set_flags),
            threading.Thread(target=read_flags),
            threading.Thread(target=read_flags),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestClockThreadSafety:
    """Clock implementations should be safe for concurrent use."""

    def test_frozen_clock_concurrent_reads(self):
        from datetime import datetime

        clock = FrozenClock(datetime(2024, 1, 1, 0, 0, 0))
        errors = []

        def read():
            try:
                for _ in range(500):
                    _ = clock.now()
                    _ = clock.utcnow()
                    _ = clock.timestamp()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=read) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestIdGeneratorThreadSafety:
    """IdGenerator must be safe for concurrent use."""

    def test_uuid_generator_concurrent(self):
        generator = UuidGenerator()
        ids = []
        lock = threading.Lock()
        errors = []

        def generate():
            try:
                for _ in range(100):
                    uid = generator.generate()
                    with lock:
                        ids.append(uid)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=generate) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # Verify all IDs are unique
        assert len(ids) == 1000
        assert len(set(ids)) == 1000
