"""
Tests for platform/foundation/feature_flags.py

Verifies FeatureFlagProvider abstraction and InMemoryFeatureFlagProvider.
"""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[3])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

from platcore.foundation.feature_flags import (
    FeatureFlagProvider,
    InMemoryFeatureFlagProvider,
)


class TestFeatureFlagProviderAbstraction:
    """Verify that FeatureFlagProvider is abstract."""

    def test_feature_flag_provider_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            FeatureFlagProvider()  # type: ignore


class TestInMemoryFeatureFlagProvider:
    """Verify InMemoryFeatureFlagProvider operations."""

    def setup_method(self):
        self.provider = InMemoryFeatureFlagProvider()

    def test_default_flags_are_disabled(self):
        assert self.provider.is_enabled("non_existent_flag") is False

    def test_default_value_returns_default(self):
        assert self.provider.get_value("non_existent", "default") == "default"

    def test_set_and_check_enabled(self):
        self.provider.set_flag("feature_x", True)
        assert self.provider.is_enabled("feature_x") is True

    def test_set_and_check_disabled(self):
        self.provider.set_flag("feature_x", False)
        assert self.provider.is_enabled("feature_x") is False

    def test_set_and_get_value(self):
        self.provider.set_flag("model_version", "v2")
        assert self.provider.get_value("model_version") == "v2"

    def test_remove_flag(self):
        self.provider.set_flag("temp_feature", True)
        assert self.provider.is_enabled("temp_feature") is True
        self.provider.remove_flag("temp_feature")
        assert self.provider.is_enabled("temp_feature") is False

    def test_initial_flags_constructor(self):
        flags = {"feature_a": True, "feature_b": False, "version": "1.0"}
        provider = InMemoryFeatureFlagProvider(initial_flags=flags)
        assert provider.is_enabled("feature_a") is True
        assert provider.is_enabled("feature_b") is False
        assert provider.get_value("version") == "1.0"

    def test_truthy_values_enable_flag(self):
        self.provider.set_flag("str_value", "enabled")
        assert self.provider.is_enabled("str_value") is True

    def test_falsy_values_disable_flag(self):
        self.provider.set_flag("zero_value", 0)
        assert self.provider.is_enabled("zero_value") is False

    def test_none_value(self):
        self.provider.set_flag("none_value", None)
        assert self.provider.is_enabled("none_value") is False

    def test_get_value_returns_none_by_default(self):
        assert self.provider.get_value("no_such_flag") is None


class TestInMemoryFeatureFlagProviderThreadSafety:
    """Basic thread safety check for feature flags."""

    def test_concurrent_set_and_read(self):
        import threading

        provider = InMemoryFeatureFlagProvider()
        errors = []

        def set_flags():
            for i in range(100):
                provider.set_flag(f"flag_{i}", True)

        def read_flags():
            for i in range(100):
                provider.is_enabled(f"flag_{i}")
                provider.get_value(f"flag_{i}")

        threads = [
            threading.Thread(target=set_flags),
            threading.Thread(target=read_flags),
            threading.Thread(target=read_flags),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Verify no corruption
        for i in range(100):
            assert provider.is_enabled(f"flag_{i}") is True
