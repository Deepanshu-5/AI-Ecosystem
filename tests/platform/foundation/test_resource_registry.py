"""
Tests for platform/foundation/resource_registry.py

Verifies ResourceRegistry registration, status management, type filtering,
and thread safety.
"""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[3])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

from platcore.foundation.resource_registry import (
    ResourceMetadata,
    ResourceRegistry,
    ResourceStatus,
    ResourceType,
)
from platcore.foundation.exceptions import (
    ResourceAlreadyRegisteredError,
    ResourceNotFoundError,
)


class TestResourceRegistryRegistration:
    """Verify resource registration operations."""

    def setup_method(self):
        self.registry = ResourceRegistry()

    def test_register_resource(self):
        self.registry.register("postgres", ResourceType.DATABASE)
        assert self.registry.count == 1

    def test_register_with_metadata(self):
        self.registry.register(
            "redis",
            ResourceType.CACHE,
            description="Session cache",
            tags={"owner": "infra"},
            connection_details={"host": "localhost", "port": 6379},
        )
        meta = self.registry.get("redis")
        assert meta.name == "redis"
        assert meta.resource_type == ResourceType.CACHE
        assert meta.description == "Session cache"
        assert meta.tags == {"owner": "infra"}
        assert meta.connection_details == {"host": "localhost", "port": 6379}

    def test_duplicate_registration_raises(self):
        self.registry.register("postgres", ResourceType.DATABASE)
        with pytest.raises(ResourceAlreadyRegisteredError, match="already registered"):
            self.registry.register("postgres", ResourceType.DATABASE)

    def test_override_allows_re_registration(self):
        self.registry.register("postgres", ResourceType.DATABASE)
        self.registry.register("postgres", ResourceType.CACHE, override=True)
        assert self.registry.get("postgres").resource_type == ResourceType.CACHE

    def test_unregister_resource(self):
        self.registry.register("postgres", ResourceType.DATABASE)
        self.registry.unregister("postgres")
        assert self.registry.count == 0

    def test_unregister_not_found_raises(self):
        with pytest.raises(ResourceNotFoundError, match="not found"):
            self.registry.unregister("non_existent")

    def test_get_not_found_raises(self):
        with pytest.raises(ResourceNotFoundError, match="not found"):
            self.registry.get("non_existent")


class TestResourceRegistryStatus:
    """Verify resource status management."""

    def setup_method(self):
        self.registry = ResourceRegistry()
        self.registry.register("postgres", ResourceType.DATABASE)

    def test_default_status_is_unknown(self):
        assert self.registry.get("postgres").status == ResourceStatus.UNKNOWN

    def test_update_status(self):
        self.registry.update_status("postgres", ResourceStatus.AVAILABLE)
        assert self.registry.get("postgres").status == ResourceStatus.AVAILABLE

    def test_update_status_not_found_raises(self):
        with pytest.raises(ResourceNotFoundError):
            self.registry.update_status("non_existent", ResourceStatus.AVAILABLE)

    def test_get_by_status(self):
        self.registry.register("redis", ResourceType.CACHE)
        self.registry.update_status("redis", ResourceStatus.AVAILABLE)
        available = self.registry.get_by_status(ResourceStatus.AVAILABLE)
        assert "redis" in available
        assert "postgres" not in available


class TestResourceRegistryQueries:
    """Verify registry query operations."""

    def setup_method(self):
        self.registry = ResourceRegistry()
        self.registry.register("postgres", ResourceType.DATABASE)
        self.registry.register("redis", ResourceType.CACHE)
        self.registry.register("s3", ResourceType.FILESYSTEM)

    def test_get_by_type(self):
        dbs = self.registry.get_by_type(ResourceType.DATABASE)
        assert "postgres" in dbs
        assert "redis" not in dbs

    def test_get_all_returns_snapshot(self):
        snapshot = self.registry.get_all()
        assert len(snapshot) == 3

    def test_get_all_isolated(self):
        snapshot = self.registry.get_all()
        self.registry.register("new_resource", ResourceType.OTHER)
        assert "new_resource" not in snapshot

    def test_count(self):
        assert self.registry.count == 3
        self.registry.unregister("postgres")
        assert self.registry.count == 2

    def test_clear(self):
        self.registry.clear()
        assert self.registry.count == 0


class TestResourceRegistryThreadSafety:
    """Verify thread safety of operations."""

    def test_concurrent_registrations(self):
        import threading

        registry = ResourceRegistry()
        errors = []

        def register_resource(idx):
            try:
                registry.register(f"resource_{idx}", ResourceType.OTHER)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=register_resource, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert registry.count == 50

