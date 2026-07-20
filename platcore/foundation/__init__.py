"""
platform/foundation/__init__.py

Platform Foundation — lowest platform layer.

Exposes stable public contracts (abstractions) only. Internal
implementations may change without affecting consumers.
"""

# Exceptions
from .exceptions import (
    CircularDependencyError,
    FeatureFlagNotFoundError,
    InvalidLifecycleStateError,
    PlatformFoundationError,
    ResourceAlreadyRegisteredError,
    ResourceNotFoundError,
    ServiceAlreadyRegisteredError,
    ServiceNotFoundError,
)

# Clock
from .clock import Clock, FrozenClock, SystemClock

# Container
from .container import ServiceContainer

# Environment
from .environment import Environment, EnvironmentProvider

# Feature Flags
from .feature_flags import FeatureFlagProvider, InMemoryFeatureFlagProvider

# Identifier Generation
from .id_generator import IdGenerator, UuidGenerator

# Lifecycle
from .lifecycle import LifecycleManager, LifecycleState

# Service Registry
from .service_registry import ServiceMetadata, ServiceRegistry, ServiceStatus

# Resource Registry
from .resource_registry import (
    ResourceMetadata,
    ResourceRegistry,
    ResourceStatus,
    ResourceType,
)

__all__ = [
    # Exceptions
    "PlatformFoundationError",
    "ServiceNotFoundError",
    "ServiceAlreadyRegisteredError",
    "CircularDependencyError",
    "ResourceNotFoundError",
    "ResourceAlreadyRegisteredError",
    "InvalidLifecycleStateError",
    "FeatureFlagNotFoundError",
    # Clock
    "Clock",
    "SystemClock",
    "FrozenClock",
    # Container
    "ServiceContainer",
    # Environment
    "Environment",
    "EnvironmentProvider",
    # Feature Flags
    "FeatureFlagProvider",
    "InMemoryFeatureFlagProvider",
    # Identifier Generation
    "IdGenerator",
    "UuidGenerator",
    # Lifecycle
    "LifecycleManager",
    "LifecycleState",
    # Service Registry
    "ServiceMetadata",
    "ServiceRegistry",
    "ServiceStatus",
    # Resource Registry
    "ResourceMetadata",
    "ResourceRegistry",
    "ResourceStatus",
    "ResourceType",
]

