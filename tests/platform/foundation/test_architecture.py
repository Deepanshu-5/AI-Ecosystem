"""
Architecture verification tests for platform/foundation.

Verifies:
- No dependencies on higher platform layers.
- No dependencies on AI-specific components.
- No circular imports within the foundation package.
- Public API is stable and matches __init__.py exports.
"""

import sys
import importlib
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[3])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest


# List of modules/packages that the foundation MUST NOT depend on
FORBIDDEN_DEPENDENCIES = [
    "planner",
    "retriever",
    "retrieval",
    "routing",
    "budgeting",
    "prompt_builder",
    "control_plane",
    "model_execution",
    "tool_execution",
    "ingestion",
    "memory",
    "conversation_memory",
    "integration",
    "llm",
    "mcp_server",
    "observability",
    "config",
    "services",
    "shared",
    "models",
    "evaluation",
]

FORBIDDEN_AI_DEPENDENCIES = [
    "langchain",
    "llama_index",
    "openai",
    "anthropic",
    "chromadb",
    "transformers",
    "torch",
    "tensorflow",
]


class TestArchitectureNoHigherLayerDependencies:
    """Verify foundation has no dependencies on higher platform layers."""

    def test_foundation_does_not_import_higher_layers(self):
        """Scan foundation module and verify no forbidden imports exist."""
        foundation_dir = Path(__file__).resolve().parents[3] / "platcore" / "foundation"
        assert foundation_dir.exists(), "Foundation directory not found"

        for pyfile in foundation_dir.glob("*.py"):
            content = pyfile.read_text(encoding="utf-8")
            for forbidden in FORBIDDEN_DEPENDENCIES:
                # Check for import statements referencing forbidden modules
                if f"import {forbidden}" in content or f"from {forbidden}" in content:
                    pytest.fail(
                        f"{pyfile.name} imports forbidden dependency: {forbidden}"
                    )

    def test_foundation_does_not_import_ai_frameworks(self):
        """Verify foundation has no AI framework dependencies."""
        foundation_dir = Path(__file__).resolve().parents[3] / "platcore" / "foundation"

        for pyfile in foundation_dir.glob("*.py"):
            content = pyfile.read_text(encoding="utf-8")
            for forbidden in FORBIDDEN_AI_DEPENDENCIES:
                if f"import {forbidden}" in content or f"from {forbidden}" in content:
                    pytest.fail(
                        f"{pyfile.name} imports forbidden AI dependency: {forbidden}"
                    )


class TestArchitectureNoCircularImports:
    """Verify the foundation package has no circular imports."""

    def test_all_modules_importable_without_error(self):
        """Import each module individually, ensuring no circular imports."""
        modules = [
            "platcore.foundation.exceptions",
            "platcore.foundation.clock",
            "platcore.foundation.id_generator",
            "platcore.foundation.environment",
            "platcore.foundation.feature_flags",
            "platcore.foundation.lifecycle",
            "platcore.foundation.service_registry",
            "platcore.foundation.resource_registry",
            "platcore.foundation.container",
            "platcore.foundation",
        ]

        for module_name in modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")
            finally:
                # Clean up from sys.modules to avoid interference
                if module_name in sys.modules:
                    del sys.modules[module_name]


class TestPublicAPIStability:
    """Verify the public API matches what is defined in __init__.py."""

    def test_public_api_symbols_match_all(self):
        """Check that __all__ is consistent and complete."""
        from platcore.foundation import __all__ as public_api
        from platcore.foundation import (
            # Exceptions
            PlatformFoundationError,
            ServiceNotFoundError,
            ServiceAlreadyRegisteredError,
            CircularDependencyError,
            ResourceNotFoundError,
            ResourceAlreadyRegisteredError,
            InvalidLifecycleStateError,
            FeatureFlagNotFoundError,
            # Clock
            Clock,
            SystemClock,
            FrozenClock,
            # Container
            ServiceContainer,
            # Environment
            Environment,
            EnvironmentProvider,
            # Feature Flags
            FeatureFlagProvider,
            InMemoryFeatureFlagProvider,
            # IdGenerator
            IdGenerator,
            UuidGenerator,
            # Lifecycle
            LifecycleManager,
            LifecycleState,
            # Service Registry
            ServiceMetadata,
            ServiceRegistry,
            ServiceStatus,
            # Resource Registry
            ResourceMetadata,
            ResourceRegistry,
            ResourceStatus,
            ResourceType,
        )

        # Verify __all__ contains all expected symbols
        expected_symbols = [
            "PlatformFoundationError",
            "ServiceNotFoundError",
            "ServiceAlreadyRegisteredError",
            "CircularDependencyError",
            "ResourceNotFoundError",
            "ResourceAlreadyRegisteredError",
            "InvalidLifecycleStateError",
            "FeatureFlagNotFoundError",
            "Clock",
            "SystemClock",
            "FrozenClock",
            "ServiceContainer",
            "Environment",
            "EnvironmentProvider",
            "FeatureFlagProvider",
            "InMemoryFeatureFlagProvider",
            "IdGenerator",
            "UuidGenerator",
            "LifecycleManager",
            "LifecycleState",
            "ServiceMetadata",
            "ServiceRegistry",
            "ServiceStatus",
            "ResourceMetadata",
            "ResourceRegistry",
            "ResourceStatus",
            "ResourceType",
        ]

        for symbol in expected_symbols:
            assert symbol in public_api, f"Missing from __all__: {symbol}"

        # Verify no extra symbols in __all__
        for symbol in public_api:
            assert symbol in expected_symbols, f"Unexpected in __all__: {symbol}"

    def test_all_public_symbols_are_importable(self):
        """Verify that every symbol in __all__ can actually be imported."""
        from platcore.foundation import __all__ as public_api

        for symbol in public_api:
            try:
                exec(f"from platcore.foundation import {symbol}")
            except ImportError as e:
                pytest.fail(f"Cannot import {symbol}: {e}")
