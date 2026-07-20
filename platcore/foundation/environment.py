"""
platform/foundation/environment.py

Environment detection abstraction.

Provides environment detection without becoming a configuration system.
The EnvironmentProvider detects which environment the platform is running
in — it does not load, store, or distribute configuration values.
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Final


class Environment(Enum):
    """
    Enumeration of supported platform environments.

    Purpose:
        Defines the known environment types. The platform behaviour may
        differ based on the active environment, but the environment
        provider itself does not define those differences.

    Values:
        DEVELOPMENT: Local development workstation.
        STAGING: Pre-production staging environment.
        PRODUCTION: Production environment.
        TEST: Automated test execution.
    """

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class EnvironmentProvider:
    """
    Environment detection provider.

    Responsibility:
        Detect and expose the current platform environment. This provider
        takes an immutable snapshot at construction time.

    This is a stable public contract.

    The provider detects the environment by examining environment variables
    in the following order of precedence:
        1. ``PLATFORM_ENVIRONMENT`` environment variable (explicit override).
        2. Common CI/CD environment variable indicators.
        3. Falls back to ``DEVELOPMENT``.

    This class does **not** load configuration, secrets, or any other
    settings. It detects the environment only.
    """

    def __init__(self, env: Environment | None = None) -> None:
        """
        Initialize the environment provider.

        Args:
            env: Optional explicit environment. If provided, this value is
                used directly without inspecting system environment variables.
                If None, detection logic is used.
        """
        if env is not None:
            self._environment: Final[Environment] = env
        else:
            self._environment = self._detect_environment()

    @property
    def environment(self) -> Environment:
        """
        Return the detected environment.

        Returns:
            The ``Environment`` enum value representing the current
            platform environment.
        """
        return self._environment

    @property
    def is_development(self) -> bool:
        """Return True if the environment is DEVELOPMENT."""
        return self._environment == Environment.DEVELOPMENT

    @property
    def is_staging(self) -> bool:
        """Return True if the environment is STAGING."""
        return self._environment == Environment.STAGING

    @property
    def is_production(self) -> bool:
        """Return True if the environment is PRODUCTION."""
        return self._environment == Environment.PRODUCTION

    @property
    def is_test(self) -> bool:
        """Return True if the environment is TEST."""
        return self._environment == Environment.TEST

    def _detect_environment(self) -> Environment:
        """
        Detect the current environment from system environment variables.

        Detection order:
            1. ``PLATFORM_ENVIRONMENT`` — explicit override.
            2. ``ENVIRONMENT`` — alternative explicit override.
            3. Common CI/CD indicators (``CI``, ``PYTEST_CURRENT_TEST``).
            4. Default to ``DEVELOPMENT``.

        Returns:
            The detected ``Environment`` enum value.
        """
        # Check for explicit environment variable override
        env_var = os.environ.get("PLATFORM_ENVIRONMENT") or os.environ.get(
            "ENVIRONMENT"
        )
        if env_var is not None:
            normalized = env_var.strip().lower()
            for env in Environment:
                if env.value == normalized:
                    return env

        # Detect test environment
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return Environment.TEST

        # Detect CI environment
        if os.environ.get("CI"):
            return Environment.STAGING

        # Default
        return Environment.DEVELOPMENT
