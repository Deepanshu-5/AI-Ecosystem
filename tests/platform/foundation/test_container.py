"""
Tests for platform/foundation/container.py

Verifies ServiceContainer registration, resolution, constructor DI,
circular dependency detection, singleton/transient lifecycles, and
parent container hierarchy.
"""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[3])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from abc import ABC, abstractmethod

import pytest

from platcore.foundation.container import ServiceContainer
from platcore.foundation.exceptions import (
    CircularDependencyError,
    ServiceAlreadyRegisteredError,
    ServiceNotFoundError,
)
from platcore.foundation.clock import Clock, SystemClock
from platcore.foundation.id_generator import IdGenerator, UuidGenerator


# Test interfaces and implementations
class _Logger(ABC):
    @abstractmethod
    def log(self, message: str) -> None: ...

class _ConsoleLogger(_Logger):
    def __init__(self, prefix: str = "[LOG]") -> None:
        self.prefix = prefix

    def log(self, message: str) -> None:
        pass  # No-op for testing

class _Database:
    def __init__(self, connection_string: str = "default") -> None:
        self.connection_string = connection_string

class _ServiceA:
    def __init__(self, logger: _Logger, clock: Clock) -> None:
        self.logger = logger
        self.clock = clock

class _ServiceB:
    def __init__(self, service_a: _ServiceA) -> None:
        self.service_a = service_a

class _CircularA:
    def __init__(self, b: "_CircularB") -> None:
        self.b = b

class _CircularB:
    def __init__(self, a: _CircularA) -> None:
        self.a = a


# Non-forward-reference circular dependency for DI detection
class _DirectCircularA:
    def __init__(self, b: "_DirectCircularB") -> None:
        self.b = b  # type: ignore

class _DirectCircularB:
    def __init__(self, a: "_DirectCircularA") -> None:
        self.a = a  # type: ignore


class TestServiceContainerRegistration:
    """Verify service registration."""

    def setup_method(self):
        self.container = ServiceContainer()

    def test_register_interface_and_implementation(self):
        self.container.register(_Logger, _ConsoleLogger)
        assert self.container.is_registered(_Logger) is True

    def test_register_self_as_implementation(self):
        self.container.register(_ConsoleLogger)
        assert self.container.is_registered(_ConsoleLogger) is True

    def test_register_instance(self):
        logger = _ConsoleLogger()
        self.container.register(_Logger, logger)
        resolved = self.container.resolve(_Logger)
        assert resolved is logger  # Same instance

    def test_duplicate_registration_raises(self):
        self.container.register(_Logger, _ConsoleLogger)
        with pytest.raises(ServiceAlreadyRegisteredError, match="already registered"):
            self.container.register(_Logger, _ConsoleLogger)

    def test_override_allows_re_registration(self):
        self.container.register(_Logger, _ConsoleLogger)
        self.container.register(_Logger, _ConsoleLogger, override=True)
        assert self.container.is_registered(_Logger) is True

    def test_is_registered_returns_false_for_unregistered(self):
        assert self.container.is_registered(_Logger) is False

    def test_unregister_removes_service(self):
        self.container.register(_Logger, _ConsoleLogger)
        self.container.unregister(_Logger)
        assert self.container.is_registered(_Logger) is False

    def test_unregister_unregistered_raises(self):
        with pytest.raises(ServiceNotFoundError):
            self.container.unregister(_Logger)

    def test_clear_removes_all(self):
        self.container.register(_Logger, _ConsoleLogger)
        self.container.register(IdGenerator, UuidGenerator)
        self.container.clear()
        assert self.container.is_registered(_Logger) is False
        assert self.container.is_registered(IdGenerator) is False


class TestServiceContainerResolution:
    """Verify service resolution."""

    def setup_method(self):
        self.container = ServiceContainer()

    def test_resolve_singleton_returns_same_instance(self):
        self.container.register(_Logger, _ConsoleLogger)
        instance1 = self.container.resolve(_Logger)
        instance2 = self.container.resolve(_Logger)
        assert instance1 is instance2

    def test_resolve_transient_returns_new_instance(self):
        self.container.register(_Logger, _ConsoleLogger, singleton=False)
        instance1 = self.container.resolve(_Logger)
        instance2 = self.container.resolve(_Logger)
        assert instance1 is not instance2

    def test_resolve_instance_returns_same(self):
        logger = _ConsoleLogger()
        self.container.register(_Logger, logger)
        assert self.container.resolve(_Logger) is logger

    def test_resolve_unregistered_raises(self):
        with pytest.raises(ServiceNotFoundError, match="No service registered"):
            self.container.resolve(_Logger)


class TestServiceContainerConstructorDI:
    """Verify constructor dependency injection."""

    def setup_method(self):
        self.container = ServiceContainer()
        self.container.register(_Logger, _ConsoleLogger)
        self.container.register(Clock, SystemClock)
        self.container.register(IdGenerator, UuidGenerator)

    def test_injects_constructor_dependencies(self):
        self.container.register(_ServiceA)
        service_a = self.container.resolve(_ServiceA)
        assert isinstance(service_a, _ServiceA)
        assert isinstance(service_a.logger, _ConsoleLogger)
        assert isinstance(service_a.clock, SystemClock)

    def test_chained_dependency_injection(self):
        self.container.register(_ServiceA)
        self.container.register(_ServiceB)
        service_b = self.container.resolve(_ServiceB)
        assert isinstance(service_b, _ServiceB)
        assert isinstance(service_b.service_a, _ServiceA)

    def test_circular_dependency_detected(self):
        self.container.register(_DirectCircularA)
        self.container.register(_DirectCircularB)
        with pytest.raises(CircularDependencyError, match="Circular dependency"):
            self.container.resolve(_DirectCircularA)

    def test_constructor_with_defaults_uses_default(self):
        self.container.register(_Database)
        db = self.container.resolve(_Database)
        assert db.connection_string == "default"

    def test_partial_injection(self):
        """If a service isn't registered for a parameter with a default,
        the default should be preserved."""
        self.container.register(_Database)
        db = self.container.resolve(_Database)
        assert db.connection_string == "default"


class TestServiceContainerParent:
    """Verify parent container hierarchy."""

    def test_resolve_from_parent(self):
        parent = ServiceContainer()
        parent.register(_Logger, _ConsoleLogger)
        child = ServiceContainer(parent=parent)
        assert child.is_registered(_Logger) is True
        logger = child.resolve(_Logger)
        assert isinstance(logger, _ConsoleLogger)

    def test_child_override_does_not_affect_parent(self):
        parent = ServiceContainer()
        parent.register(_Logger, _ConsoleLogger)
        child = ServiceContainer(parent=parent)
        class _OtherLogger(_Logger):
            def log(self, message: str) -> None: ...
        child.register(_Logger, _OtherLogger, override=True)
        parent_logger = parent.resolve(_Logger)
        child_logger = child.resolve(_Logger)
        assert isinstance(parent_logger, _ConsoleLogger)
        assert isinstance(child_logger, _OtherLogger)

