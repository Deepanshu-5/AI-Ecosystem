"""
platform/foundation/feature_flags.py

Feature flag abstraction and default in-memory implementation.

Provides a simple, provider-agnostic FeatureFlagProvider interface that
allows platform behaviour to be toggled without code changes.
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from typing import Any, Final


class FeatureFlagProvider(ABC):
    """
    Abstract feature flag provider.

    Responsibility:
        Determine whether a given feature is enabled and provide optional
        feature-specific configuration values.

    This is a stable public contract. Consumers depend on this abstraction,
    not on any concrete implementation.
    """

    @abstractmethod
    def is_enabled(self, flag_name: str) -> bool:
        """
        Check whether the specified feature flag is enabled.

        Args:
            flag_name: The name of the feature flag to check.

        Returns:
            ``True`` if the feature is enabled, ``False`` otherwise.
        """

    @abstractmethod
    def get_value(self, flag_name: str, default: Any = None) -> Any:
        """
        Retrieve the value associated with a feature flag, if any.

        Args:
            flag_name: The name of the feature flag.
            default: The default value to return if the flag has no
                associated value or does not exist.

        Returns:
            The feature flag value, or ``default`` if not found.
        """


class InMemoryFeatureFlagProvider(FeatureFlagProvider):
    """
    In-memory feature flag provider.

    Stores feature flags in a thread-safe dictionary. This is suitable
    for development, testing, and simple production scenarios where flags
    are set programmatically.

    This class is part of the internal implementation, not the public
    contract. Consumers should depend on ``FeatureFlagProvider``.
    """

    def __init__(self, initial_flags: dict[str, Any] | None = None) -> None:
        """
        Initialize the in-memory feature flag provider.

        Args:
            initial_flags: Optional dictionary of initial flag names to
                values. A flag is considered enabled if its value is
                truthy.
        """
        self._flags: dict[str, Any] = {}
        self._lock: Final = threading.Lock()

        if initial_flags:
            with self._lock:
                self._flags.update(initial_flags)

    def is_enabled(self, flag_name: str) -> bool:
        with self._lock:
            return bool(self._flags.get(flag_name, False))

    def get_value(self, flag_name: str, default: Any = None) -> Any:
        with self._lock:
            return self._flags.get(flag_name, default)

    def set_flag(self, flag_name: str, value: Any) -> None:
        """
        Set a feature flag value.

        Args:
            flag_name: The name of the feature flag.
            value: The value to set. A truthy value enables the flag.
        """
        with self._lock:
            self._flags[flag_name] = value

    def remove_flag(self, flag_name: str) -> None:
        """
        Remove a feature flag.

        Args:
            flag_name: The name of the feature flag to remove.
        """
        with self._lock:
            self._flags.pop(flag_name, None)

