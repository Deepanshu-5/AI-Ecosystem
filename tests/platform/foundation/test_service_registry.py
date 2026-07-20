"""
Tests for platform/foundation/service_registry.py

Verifies ServiceRegistry registration, lookup, status management, and
thread safety.
"""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[3])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

from platcore.foundation.service_registry import (
    ServiceMetadata,
    ServiceRegistry,
    ServiceStatus,
)
from platcore.foundation.exceptions import (
    ServiceAlreadyRegisteredError,
    ServiceNotFoundError,
)


class TestServiceRegistryRegistration:
    """Verify service registration operations."""

    def setup_method(self):
        self.registry = ServiceRegistry()

    def test_register_service(self):
        self.registry.register("planner", str)
        assert self.registry.count == 1

    def test_register_with_metadata(self):
        self.registry.register("planner", str, version="1.0", tags={"owner": "core"})
        meta = self.registry.get("planner")
        assert meta.name == "planner"
        assert meta.service_type is str
        assert meta.version == "1.0"
        assert meta.tags == {"owner": "core"}

    def test_duplicate_registration_raises(self):
        self.registry.register("planner", str)
        with pytest.raises(ServiceAlreadyRegisteredError, match="already registered"):
            self.registry.register("planner", int)

    def test_override_allows_re_registration(self):
        self.registry.register("planner", str)
        self.registry.register("planner", int, override=True)
        meta = self.registry.get("planner")
        assert meta.service_type is int

    def test_unregister_service(self):
        self.registry.register("planner", str)
        self.registry.unregister("planner")
        assert self.registry.count == 0

    def test_unregister_unregistered_raises(self):
        with pytest.raises(ServiceNotFoundError, match="not found"):
            self.registry.unregister("non_existent")

    def test_get_unregistered_raises(self):
        with pytest.raises(ServiceNotFoundError, match="not found"):
            self.registry.get("non_existent")


class TestServiceRegistryStatus:
    """Verify service status management."""

    def setup_method(self):
        self.registry = ServiceRegistry()
        self.registry.register("planner", str)

    def test_default_status_is_registered(self):
        meta = self.registry.get("planner")
        assert meta.status == ServiceStatus.REGISTERED

    def test_update_status(self):
        self.registry.update_status("planner", ServiceStatus.RUNNING)
        assert self.registry.get("planner").status == ServiceStatus.RUNNING

    def test_update_status_unregistered_raises(self):
        with pytest.raises(ServiceNotFoundError):
            self.registry.update_status("non_existent", ServiceStatus.RUNNING)

    def test_get_by_status(self):
        self.registry.register("retriever", int)
        self.registry.update_status("retriever", ServiceStatus.RUNNING)
        running = self.registry.get_by_status(ServiceStatus.RUNNING)
        assert "retriever" in running
        assert "planner" not in running


class TestServiceRegistryQueries:
    """Verify registry query operations."""

    def setup_method(self):
        self.registry = ServiceRegistry()
        self.registry.register("planner", str)
        self.registry.register("retriever", int)
        self.registry.register("router", float, version="2.0")

    def test_get_all_returns_snapshot(self):
        all_services = self.registry.get_all()
        assert len(all_services) == 3
        assert "planner" in all_services

    def test_get_all_isolated_from_mutations(self):
        snapshot = self.registry.get_all()
        self.registry.register("new_service", dict)
        # Snapshot should be unchanged
        assert "new_service" not in snapshot

    def test_count(self):
        assert self.registry.count == 3
        self.registry.unregister("planner")
        assert self.registry.count == 2

    def test_clear(self):
        self.registry.clear()
        assert self.registry.count == 0


class TestServiceRegistryThreadSafety:
    """Verify thread safety of operations."""

    def test_concurrent_registrations(self):
        import threading

        registry = ServiceRegistry()
        errors = []

        def register_service(idx):
            try:
                registry.register(f"service_{idx}", str)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=register_service, args=(i,)) for i in range(50)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert registry.count == 50
