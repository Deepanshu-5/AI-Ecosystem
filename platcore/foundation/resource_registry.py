"""
platform/foundation/resource_registry.py

Resource Registry for external resources (databases, caches, filesystems,
APIs, etc.).

The ResourceRegistry tracks external resources that the platform depends
on. This is separate from the ServiceRegistry which tracks platform
internal services managed by DI.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field,replace
from enum import Enum, auto
from typing import Any, Final

from .exceptions import (
    ResourceAlreadyRegisteredError,
    ResourceNotFoundError,
)


class ResourceStatus(Enum):
    """
    Enumeration of possible resource health statuses.

    Values:
        UNKNOWN: Resource status has not been determined.
        AVAILABLE: Resource is available and operational.
        UNAVAILABLE: Resource is not currently available.
        DEGRADED: Resource is operational but degraded.
        FAILED: Resource has failed.
    """

    UNKNOWN = auto()
    AVAILABLE = auto()
    UNAVAILABLE = auto()
    DEGRADED = auto()
    FAILED = auto()


class ResourceType(Enum):
    """
    Enumeration of known resource types.

    Values:
        DATABASE: Database resource (relational, document, vector, etc.).
        CACHE: Cache resource (Redis, Memcached, in-memory, etc.).
        FILESYSTEM: Filesystem or blob storage resource.
        API: External API or web service.
        MESSAGE_QUEUE: Message queue or event bus.
        OTHER: Any other external resource type.
    """

    DATABASE = auto()
    CACHE = auto()
    FILESYSTEM = auto()
    API = auto()
    MESSAGE_QUEUE = auto()
    OTHER = auto()


@dataclass(frozen=True)
class ResourceMetadata:
    """
    Metadata associated with a registered resource.

    Attributes:
        name: The unique name of the resource.
        resource_type: The type of the resource.
        description: Optional human-readable description.
        status: Current health status.
        tags: Optional dictionary of arbitrary metadata tags.
        connection_details: Optional dictionary of connection information
            (URLs, endpoints, etc.). This should not contain secrets.
    """

    name: str
    resource_type: ResourceType
    description: str | None = None
    status: ResourceStatus = ResourceStatus.UNKNOWN
    tags: dict[str, Any] = field(default_factory=dict)
    connection_details: dict[str, Any] = field(default_factory=dict)


class ResourceRegistry:
    """
    External resource registry.

    Responsibility:
        Track external resources that the platform depends on, their
        types, health status, and metadata.

    The ResourceRegistry is separate from the ServiceRegistry.
    ServiceRegistry tracks platform-internal services; ResourceRegistry
    tracks external dependencies (databases, caches, APIs, etc.).

    Thread safety:
        All operations are protected by a reentrant lock.

    This is a stable public contract.
    """

    def __init__(self) -> None:
        self._resources: dict[str, ResourceMetadata] = {}
        self._lock: Final = threading.RLock()

    def register(
        self,
        name: str,
        resource_type: ResourceType,
        description: str | None = None,
        tags: dict[str, Any] | None = None,
        connection_details: dict[str, Any] | None = None,
        override: bool = False,
    ) -> None:
        """
        Register a resource with the registry.

        Args:
            name: The unique name of the resource.
            resource_type: The ``ResourceType`` of the resource.
            description: Optional human-readable description.
            tags: Optional dictionary of arbitrary metadata tags.
            connection_details: Optional dictionary of connection information.
                Should not contain secrets.
            override: If True, allows replacing an existing registration.
                If False (default), raises ``ResourceAlreadyRegisteredError``
                if a resource with the same name exists.

        Raises:
            ResourceAlreadyRegisteredError: If a resource with the same name
                is already registered and ``override`` is False.
        """
        with self._lock:
            if name in self._resources and not override:
                raise ResourceAlreadyRegisteredError(
                    f"Resource '{name}' is already registered. "
                    "Use override=True to replace."
                )

            self._resources[name] = ResourceMetadata(
                name=name,
                resource_type=resource_type,
                description=description,
                tags=dict(tags) if tags is not None else {},
                connection_details=(
                 dict(connection_details)
                    if connection_details is not None
                    else {}
                ),
            )            

    def unregister(self, name: str) -> None:
        """
        Remove a resource registration.

        Args:
            name: The name of the resource to unregister.

        Raises:
            ResourceNotFoundError: If no resource with the given name exists.
        """
        with self._lock:
            if name not in self._resources:
                raise ResourceNotFoundError(f"Resource '{name}' not found in registry")
            del self._resources[name]

    def get(self, name: str) -> ResourceMetadata:
        """
        Get metadata for a registered resource.

        Args:
            name: The name of the resource.

        Returns:
            The ``ResourceMetadata`` for the resource.

        Raises:
            ResourceNotFoundError: If no resource with the given name exists.
        """
        with self._lock:
            if name not in self._resources:
                raise ResourceNotFoundError(f"Resource '{name}' not found in registry")
            return self._resources[name]

    def update_status(self, name: str, status: ResourceStatus) -> None:
        """
        Update the health status of a registered resource.

        Args:
            name: The name of the resource.
            status: The new ``ResourceStatus``.

        Raises:
            ResourceNotFoundError: If no resource with the given name exists.
        """
        with self._lock:
            if name not in self._resources:
                raise ResourceNotFoundError(f"Resource '{name}' not found in registry")
            self._resources[name] = replace(
                self._resources[name],
                status=status,
        )
    def get_all(self) -> dict[str, ResourceMetadata]:
        """
        Get a snapshot of all registered resources.

        Returns:
            A dictionary mapping resource name to ``ResourceMetadata``.
        """
        with self._lock:
            return dict(self._resources)

    def get_by_type(self, resource_type: ResourceType) -> dict[str, ResourceMetadata]:
        """
        Get all resources of the given type.

        Args:
            resource_type: The ``ResourceType`` to filter by.

        Returns:
            A dictionary of resource name to ``ResourceMetadata`` for
            resources matching the type.
        """
        with self._lock:
            return {
                name: meta
                for name, meta in self._resources.items()
                if meta.resource_type == resource_type
            }

    def get_by_status(self, status: ResourceStatus) -> dict[str, ResourceMetadata]:
        """
        Get all resources with the given status.

        Args:
            status: The ``ResourceStatus`` to filter by.

        Returns:
            A dictionary of resource name to ``ResourceMetadata`` for
            resources matching the status.
        """
        with self._lock:
            return {
                name: meta
                for name, meta in self._resources.items()
                if meta.status == status
            }

    def clear(self) -> None:
        """Remove all resource registrations."""
        with self._lock:
            self._resources.clear()

    @property
    def count(self) -> int:
        """Return the number of registered resources."""
        with self._lock:
            return len(self._resources)
