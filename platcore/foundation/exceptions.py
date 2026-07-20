"""
platform/foundation/exceptions.py

Domain exceptions raised by the Platform Foundation package.

This is the lowest exception hierarchy in the platform. No higher platform
layer depends on it; instead, higher-layer exceptions inherit from their
own base classes.
"""


class PlatformFoundationError(Exception):
    """
    Base exception for all domain violations raised within the Platform
    Foundation package.

    Purpose:
        Provides a single, importable root so callers can catch every
        Platform Foundation failure without depending on built-in exception
        types (ValueError, TypeError, RuntimeError).

    Owned by:
        platform/foundation/exceptions.py

    Invariants:
        - Carries a human-readable, deterministic message.
        - Never wraps or leaks infrastructure-level stack traces.
    """


class ServiceNotFoundError(PlatformFoundationError):
    """
    Raised when a service is requested from the ServiceContainer or
    ServiceRegistry but no matching registration exists.

    Purpose:
        Signals that the requested service interface has not been registered.
        The caller must ensure registration before resolution.

    Owned by:
        platform/foundation/exceptions.py
    """


class ServiceAlreadyRegisteredError(PlatformFoundationError):
    """
    Raised when a service is registered under an interface that already has
    a registered implementation and override was not explicitly requested.

    Purpose:
        Prevents accidental duplicate registrations in the ServiceContainer
        or ServiceRegistry.

    Owned by:
        platform/foundation/exceptions.py
    """


class CircularDependencyError(PlatformFoundationError):
    """
    Raised when a circular dependency is detected during service resolution
    in the ServiceContainer.

    Purpose:
        Prevents infinite recursion or deadlock caused by circular service
        dependencies.

    Owned by:
        platform/foundation/exceptions.py
    """


class ResourceNotFoundError(PlatformFoundationError):
    """
    Raised when a resource is requested from the ResourceRegistry but no
    matching registration exists.

    Purpose:
        Signals that the requested resource has not been registered.

    Owned by:
        platform/foundation/exceptions.py
    """


class ResourceAlreadyRegisteredError(PlatformFoundationError):
    """
    Raised when a resource is registered under an identifier that already
    exists and override was not explicitly requested.

    Purpose:
        Prevents accidental duplicate resource registrations.

    Owned by:
        platform/foundation/exceptions.py
    """


class InvalidLifecycleStateError(PlatformFoundationError):
    """
    Raised when a lifecycle state transition is invalid.

    Purpose:
        Signals that a requested state change violates the monotonic
        lifecycle progression rules.

    Owned by:
        platform/foundation/exceptions.py
    """


class FeatureFlagNotFoundError(PlatformFoundationError):
    """
    Raised when a feature flag is queried but has not been registered.

    Purpose:
        Signals that the requested feature flag does not exist.

    Owned by:
        platform/foundation/exceptions.py
    """

