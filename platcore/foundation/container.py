"""
platform/foundation/container.py

Dependency injection container.

Provides a ServiceContainer that supports constructor dependency injection
with circular dependency detection and duplicate registration prevention.
"""

from __future__ import annotations

import threading
import typing
from typing import Any, Final, TypeVar

from .exceptions import (
    CircularDependencyError,
    ServiceAlreadyRegisteredError,
    ServiceNotFoundError,
)

T = TypeVar("T")

# Sentinel for tracking resolution chain (thread-local)
_resolution_chain: threading.local = threading.local()


def _get_resolution_chain() -> list[type]:
    """Get the current thread's resolution chain."""
    if not hasattr(_resolution_chain, "chain"):
        _resolution_chain.chain = []
    return _resolution_chain.chain


class _ServiceRegistration:
    """
    Internal holder for a service registration.

    Encapsulates the implementation factory, singleton instance, and
    lifecycle metadata for a registered service.
    """

    __slots__ = ("factory", "singleton", "_instance", "_lock")

    def __init__(self, factory: type | object, singleton: bool) -> None:
        self.factory = factory
        self.singleton = singleton
        self._instance: Any | None = None
        self._lock = threading.Lock() if singleton else None

    def resolve(self, container: ServiceContainer) -> Any:
        """
        Resolve the service, creating the instance if necessary.

        Args:
            container: The ServiceContainer to use for resolving
                constructor dependencies.

        Returns:
            The resolved service instance.
        """
        if self.singleton:
            with self._lock:
                if self._instance is not None:
                    return self._instance
                instance = self._create_instance(container)
                self._instance = instance
                return instance
        else:
            return self._create_instance(container)

    def _create_instance(self, container: ServiceContainer) -> Any:
        """Create a new instance of the service."""
        if isinstance(self.factory, type):
            return container._construct(self.factory)
        return self.factory


class ServiceContainer:
    """
    Dependency injection container.

    Responsibility:
        Manage service registration and resolution using constructor-based
        dependency injection. Supports singleton and transient lifecycles,
        circular dependency detection, and duplicate registration prevention.

    This is a stable public contract.
    """

    def __init__(self, parent: ServiceContainer | None = None) -> None:
        """
        Initialize the service container.

        Args:
            parent: Optional parent container for hierarchical resolution.
                If set, unresolved services are looked up in the parent.
        """
        self._registrations: dict[type, _ServiceRegistration] = {}
        self._lock: Final = threading.RLock()
        self._parent: ServiceContainer | None = parent

    def register(
        self,
        interface: type[T],
        implementation: type[T] | object | None = None,
        singleton: bool = True,
        override: bool = False,
    ) -> None:
        """
        Register a service implementation for the given interface.

        Args:
            interface: The abstract type (interface) to register against.
            implementation: The concrete implementation class or instance.
                If None, ``interface`` is used as both interface and
                implementation.
            singleton: If True (default), the same instance is returned on
                every resolution. If False, a new instance is created each
                time.
            override: If True, allows replacing an existing registration.
                If False (default), raises ``ServiceAlreadyRegisteredError``
                if ``interface`` is already registered.

        Raises:
            ServiceAlreadyRegisteredError: If ``interface`` is already
                registered and ``override`` is False.
        """
        if implementation is None:
            implementation = interface

        factory: type | object = implementation

        with self._lock:
            if interface in self._registrations and not override:
                raise ServiceAlreadyRegisteredError(
                    f"Service for {interface.__name__} is already registered. "
                    "Use override=True to replace."
                )

            self._registrations[interface] = _ServiceRegistration(
                factory=factory, singleton=singleton
            )

    def resolve(self, interface: type[T]) -> T:
        """
        Resolve a service instance for the given interface.

        Args:
            interface: The abstract type to resolve.

        Returns:
            An instance implementing ``interface``.

        Raises:
            ServiceNotFoundError: If no registration exists for ``interface``.
            CircularDependencyError: If a circular dependency is detected.
        """
        with self._lock:
            chain = _get_resolution_chain()

            # Check for circular dependency
            if interface in chain:
                chain_desc = " -> ".join(t.__name__ for t in chain + [interface])
                raise CircularDependencyError(
                    f"Circular dependency detected: {chain_desc}"
                )

            registration = self._registrations.get(interface)

            # Check parent container if not found locally
            if registration is None and self._parent is not None:
                self._lock.release()
                try:
                    return self._parent.resolve(interface)
                finally:
                    self._lock.acquire()

            if registration is None:
                raise ServiceNotFoundError(
                    f"No service registered for {interface.__name__}"
                )

            chain.append(interface)
            try:
                return registration.resolve(self)
            finally:
                chain.remove(interface)

    def is_registered(self, interface: type) -> bool:
        """
        Check whether a service is registered for the given interface.

        Args:
            interface: The abstract type to check.

        Returns:
            ``True`` if a registration exists locally or in a parent
            container.
        """
        with self._lock:
            if interface in self._registrations:
                return True
            if self._parent is not None:
                return self._parent.is_registered(interface)
            return False

    def unregister(self, interface: type) -> None:
        """
        Remove a service registration.

        Args:
            interface: The abstract type to unregister.

        Raises:
            ServiceNotFoundError: If no registration exists locally.
        """
        with self._lock:
            if interface not in self._registrations:
                raise ServiceNotFoundError(
                    f"No service registered for {interface.__name__}"
                )
            del self._registrations[interface]

    def clear(self) -> None:
        """Remove all local service registrations."""
        with self._lock:
            self._registrations.clear()

    def _construct(self, cls: type) -> Any:
        """
        Construct an instance of ``cls``, resolving constructor parameters
        from the container.

        This method inspects ``__init__`` type hints and resolves each
        parameter from the container. Parameters without type hints or
        with non-service types are left at their default values.

        Uses ``typing.get_type_hints()`` to resolve forward references
        (string annotations) to actual types.

        Args:
            cls: The class to instantiate.

        Returns:
            A new instance of ``cls``.
        """
        import inspect

        sig = inspect.signature(cls.__init__)
        kwargs: dict[str, Any] = {}

        # Resolve type hints (handles forward references from PEP 563)
        try:
            hints = typing.get_type_hints(cls.__init__)
        except Exception:
            hints = {}

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            # Get resolved type hint
            param_type = hints.get(param_name)

            if param_type is None or param_type is inspect.Parameter.empty:
                # No type hint — use default if available, otherwise skip
                if param.default is not inspect.Parameter.empty:
                    kwargs[param_name] = param.default
                continue

            # If the parameter has a default, only inject if registered
            if param.default is not inspect.Parameter.empty:
                if self.is_registered(param_type):
                    kwargs[param_name] = self.resolve(param_type)
                else:
                    kwargs[param_name] = param.default
            else:
                # Required parameter — must be resolvable
                kwargs[param_name] = self.resolve(param_type)

        return cls(**kwargs)

