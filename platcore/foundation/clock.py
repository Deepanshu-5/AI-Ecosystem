"""
platform/foundation/clock.py

Clock abstraction and implementations.

Provides a provider-agnostic Clock interface that decouples time-sensitive
operations from the system clock, enabling deterministic testing.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Final


class Clock(ABC):
    """
    Abstract clock provider.

    Responsibility:
        Provide the current time and date. All platform components that
        require time information should depend on this abstraction rather
        than directly on ``datetime`` or ``time`` modules.

    This is a stable public contract. Consumers depend on this abstraction,
    not on any concrete implementation.
    """

    @abstractmethod
    def now(self) -> datetime:
        """
        Return the current date and time in the local timezone.

        Returns:
            A ``datetime`` instance representing the current moment in the
            local timezone.
        """

    @abstractmethod
    def utcnow(self) -> datetime:
        """
        Return the current date and time in UTC.

        Returns:
            A timezone-aware ``datetime`` instance in UTC.
        """

    @abstractmethod
    def timestamp(self) -> float:
        """
        Return the current time as a UNIX timestamp (seconds since epoch).

        Returns:
            A ``float`` representing the current UNIX timestamp.
        """


class SystemClock(Clock):
    """
    Concrete clock implementation that reads from the system clock.

    This is the default production implementation. It delegates to
    ``datetime.now()`` and ``datetime.utcnow()``.

    This class is part of the internal implementation, not the public
    contract. Consumers should depend on ``Clock``.
    """

    def now(self) -> datetime:
        return datetime.now()

    def utcnow(self) -> datetime:
        return datetime.now(timezone.utc)

    def timestamp(self) -> float:
        from time import time

        return time()


class FrozenClock(Clock):
    """
    Concrete clock implementation that returns a fixed time.

    This is intended for testing scenarios where deterministic time is
    required. The frozen time is set at construction and never changes.

    This class is part of the internal implementation, not the public
    contract. Consumers should depend on ``Clock``.
    """

    def __init__(self, frozen_datetime: datetime | None = None) -> None:
        """
        Initialize the frozen clock.

        Args:
            frozen_datetime: The fixed datetime to return. If None, defaults
                to ``datetime.now(timezone.utc)`` at construction time.
        """
        if frozen_datetime is not None:
            self._frozen: Final = frozen_datetime
        else:
            self._frozen = datetime.now(timezone.utc)

    def now(self) -> datetime:
        return self._frozen

    def utcnow(self) -> datetime:
        # Ensure UTC timezone awareness
        if self._frozen.tzinfo is None:
            return self._frozen.replace(tzinfo=timezone.utc)
        return self._frozen.astimezone(timezone.utc)

    def timestamp(self) -> float:
        return self._frozen.timestamp()

