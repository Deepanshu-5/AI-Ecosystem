"""
platform/foundation/service_registry.py

Service Registry for platform services managed by DI.

The ServiceRegistry tracks platform services (their registration, status,
and metadata) without owning the DI container itself. Services are
registered here for discovery and observability, while the ServiceContainer
handles resolution.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field, replace
from enum import Enum, auto
from typing import Any, Final

from .exceptions import (
    ServiceAlreadyRegisteredError,
    ServiceNotFoundError,
)


class ServiceStatus(Enum):
    """
    Enumeration of possible service statuses.

    Values:
        REGISTERED: Service has been registered but not yet initialized.
        INITIALIZED: Service has been initialized and is ready.
        RUNNING: Service is actively running.
        STOPPED: Service has been stopped.
        FAILED: Service has entered a failed state.
    """

    REGISTERED = auto()
    INITIALIZED = auto()
    RUNNING = auto()
    STOPPED = auto()
    FAILED = auto()


@dataclass(frozen=True)
class ServiceMetadata:
    """
    Metadata associated with a registered service.

    Attributes:
        name: The human-readable name of the service.
        service_type: The class/type of the registered service.
        version: Optional version string.
        status: Current service status.
        tags: Optional dictionary of arbitrary metadata tags.
    """

    name: str
    service_type: type
    version: str | None = None
    status: ServiceStatus = ServiceStatus.REGISTERED
    tags: dict[str, Any] = field(default_factory=dict)


class ServiceRegistry:
    """
    Platform service registry.

    Responsibility:
        Track platform services, their status, and metadata. This is used
        for service discovery, observability, and lifecycle management.

    The ServiceRegistry is separate from the ServiceContainer. The container
    handles DI resolution; the registry tracks service presence and health.

    Thread safety:
        All operations are protected by a reentrant lock.

    This is a stable public contract.
    """

    def __init__(self) -> None:
        self._services: dict[str, ServiceMetadata] = {}
        self._lock: Final = threading.RLock()

    def register(
        self,
        name: str,
        service_type: type,
        version: str | None = None,
        tags: dict[str, Any] | None = None,
        override: bool = False,
    ) -> None:
        """
        Register a service with the registry.

        Args:
            name: The unique name of the service.
            service_type: The class/type of the service.
            version: Optional version string.
            tags: Optional dictionary of arbitrary metadata tags.
            override: If True, allows replacing an existing registration.
                If False (default), raises ``ServiceAlreadyRegisteredError``
                if a service with the same name exists.

        Raises:
            ServiceAlreadyRegisteredError: If a service with the same name
                is already registered and ``override`` is False.
        """
        with self._lock:
            if name in self._services and not override:
                raise ServiceAlreadyRegisteredError(
                    f"Service '{name}' is already registered. "
                    "Use override=True to replace."
                )

            self._services[name] = ServiceMetadata(
                name=name,
                service_type=service_type,
                version=version,
                tags=dict(tags) if tags is not None else {},
            )

    def unregister(self, name: str) -> None:
        """
        Remove a service registration.

        Args:
            name: The name of the service to unregister.

        Raises:
            ServiceNotFoundError: If no service with the given name exists.
        """
        with self._lock:
            if name not in self._services:
                raise ServiceNotFoundError(f"Service '{name}' not found in registry")
            del self._services[name]

    def get(self, name: str) -> ServiceMetadata:
        """
        Get metadata for a registered service.

        Args:
            name: The name of the service.

        Returns:
            The ``ServiceMetadata`` for the service.

        Raises:
            ServiceNotFoundError: If no service with the given name exists.
        """
        with self._lock:
            if name not in self._services:
                raise ServiceNotFoundError(f"Service '{name}' not found in registry")
            return self._services[name]

    def update_status(self, name: str, status: ServiceStatus) -> None:
        """
        Update the status of a registered service.

        Args:
            name: The name of the service.
            status: The new ``ServiceStatus``.

        Raises:
            ServiceNotFoundError: If no service with the given name exists.
        """
        with self._lock:
            if name not in self._services:
                raise ServiceNotFoundError(f"Service '{name}' not found in registry")
            self._services[name] = replace(
                self._services[name],
                status=status,
            )

    def get_all(self) -> dict[str, ServiceMetadata]:
        """
        Get a snapshot of all registered services.

        Returns:
            A dictionary mapping service name to ``ServiceMetadata``.
        """
        with self._lock:
            return dict(self._services)

    def get_by_status(self, status: ServiceStatus) -> dict[str, ServiceMetadata]:
        """
        Get all services with the given status.

        Args:
            status: The ``ServiceStatus`` to filter by.

        Returns:
            A dictionary of service name to ``ServiceMetadata`` for
            services matching the status.
        """
        with self._lock:
            return {
                name: meta
                for name, meta in self._services.items()
                if meta.status == status
            }

    def clear(self) -> None:
        """Remove all service registrations."""
        with self._lock:
            self._services.clear()

    @property
    def count(self) -> int:
        """Return the number of registered services."""
        with self._lock:
            return len(self._services)
