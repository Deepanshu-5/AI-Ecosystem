"""
Tests for platform/foundation/environment.py

Verifies EnvironmentProvider detection logic and convenience properties.
"""

import sys
import os
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[3])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

from platcore.foundation.environment import Environment, EnvironmentProvider


class TestEnvironmentEnum:
    """Verify Environment enum values."""

    def test_development_value(self):
        assert Environment.DEVELOPMENT.value == "development"

    def test_staging_value(self):
        assert Environment.STAGING.value == "staging"

    def test_production_value(self):
        assert Environment.PRODUCTION.value == "production"

    def test_test_value(self):
        assert Environment.TEST.value == "test"


class TestEnvironmentProviderExplicit:
    """Verify explicit environment setting."""

    def test_explicit_production(self):
        provider = EnvironmentProvider(Environment.PRODUCTION)
        assert provider.environment == Environment.PRODUCTION

    def test_explicit_development(self):
        provider = EnvironmentProvider(Environment.DEVELOPMENT)
        assert provider.environment == Environment.DEVELOPMENT

    def test_explicit_test(self):
        provider = EnvironmentProvider(Environment.TEST)
        assert provider.environment == Environment.TEST

    def test_explicit_staging(self):
        provider = EnvironmentProvider(Environment.STAGING)
        assert provider.environment == Environment.STAGING


class TestEnvironmentProviderConvenience:
    """Verify convenience properties."""

    def test_is_development_true(self):
        provider = EnvironmentProvider(Environment.DEVELOPMENT)
        assert provider.is_development is True
        assert provider.is_staging is False
        assert provider.is_production is False
        assert provider.is_test is False

    def test_is_production_true(self):
        provider = EnvironmentProvider(Environment.PRODUCTION)
        assert provider.is_production is True
        assert provider.is_development is False
        assert provider.is_test is False

    def test_is_staging_true(self):
        provider = EnvironmentProvider(Environment.STAGING)
        assert provider.is_staging is True

    def test_is_test_true(self):
        provider = EnvironmentProvider(Environment.TEST)
        assert provider.is_test is True


class TestEnvironmentProviderDetection:
    """Verify environment variable detection logic."""

    def test_platform_environment_var(self, monkeypatch):
        monkeypatch.setenv("PLATFORM_ENVIRONMENT", "production")
        provider = EnvironmentProvider()
        assert provider.environment == Environment.PRODUCTION

    def test_environment_var(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "staging")
        provider = EnvironmentProvider()
        assert provider.environment == Environment.STAGING

    def test_platform_env_takes_precedence(self, monkeypatch):
        monkeypatch.setenv("PLATFORM_ENVIRONMENT", "production")
        monkeypatch.setenv("ENVIRONMENT", "development")
        provider = EnvironmentProvider()
        assert provider.environment == Environment.PRODUCTION

    def test_test_detection_via_pytest(self, monkeypatch):
        monkeypatch.setenv(
            "PYTEST_CURRENT_TEST", "test_environment.py::test_test_detection_via_pytest"
        )
        provider = EnvironmentProvider()
        assert provider.environment == Environment.TEST

    def test_ci_detection(self, monkeypatch):
        monkeypatch.setenv("CI", "true")
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        provider = EnvironmentProvider()
        assert provider.environment == Environment.STAGING

    def test_default_development(self, monkeypatch):
        # Remove any env vars that might influence detection
        monkeypatch.delenv("PLATFORM_ENVIRONMENT", raising=False)
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        provider = EnvironmentProvider()
        assert provider.environment == Environment.DEVELOPMENT

    def test_immutable_snapshot(self):
        """The environment should be set at construction and not change."""
        provider = EnvironmentProvider(Environment.DEVELOPMENT)
        assert provider.environment == Environment.DEVELOPMENT
        # Prove it's still development (immutable behavior)
        assert not provider.is_production
