"""
Tests for platform/foundation/exceptions.py

Verifies the exception hierarchy and message conventions.
"""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[3])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

from platcore.foundation.exceptions import (
    CircularDependencyError,
    FeatureFlagNotFoundError,
    InvalidLifecycleStateError,
    PlatformFoundationError,
    ResourceAlreadyRegisteredError,
    ResourceNotFoundError,
    ServiceAlreadyRegisteredError,
    ServiceNotFoundError,
)


class TestPlatformFoundationExceptions:
    """Verify that all exceptions inherit from PlatformFoundationError."""

    def test_platform_foundation_error_is_base(self):
        assert issubclass(PlatformFoundationError, Exception)

    def test_service_not_found_inheritance(self):
        assert issubclass(ServiceNotFoundError, PlatformFoundationError)

    def test_service_already_registered_inheritance(self):
        assert issubclass(ServiceAlreadyRegisteredError, PlatformFoundationError)

    def test_circular_dependency_inheritance(self):
        assert issubclass(CircularDependencyError, PlatformFoundationError)

    def test_resource_not_found_inheritance(self):
        assert issubclass(ResourceNotFoundError, PlatformFoundationError)

    def test_resource_already_registered_inheritance(self):
        assert issubclass(ResourceAlreadyRegisteredError, PlatformFoundationError)

    def test_invalid_lifecycle_state_inheritance(self):
        assert issubclass(InvalidLifecycleStateError, PlatformFoundationError)

    def test_feature_flag_not_found_inheritance(self):
        assert issubclass(FeatureFlagNotFoundError, PlatformFoundationError)

    def test_exception_message_carries_information(self):
        msg = "Test error message"
        exc = ServiceNotFoundError(msg)
        assert str(exc) == msg

    def test_all_exceptions_carry_message(self):
        for exc_cls in [
            ServiceNotFoundError,
            ServiceAlreadyRegisteredError,
            CircularDependencyError,
            ResourceNotFoundError,
            ResourceAlreadyRegisteredError,
            InvalidLifecycleStateError,
            FeatureFlagNotFoundError,
        ]:
            exc = exc_cls("message")
            assert str(exc) == "message"
