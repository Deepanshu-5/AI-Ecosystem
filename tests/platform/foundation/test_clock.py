"""
Tests for platform/foundation/clock.py

Verifies Clock abstraction, SystemClock, and FrozenClock implementations.
"""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[3])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from datetime import datetime, timezone

import pytest

from platcore.foundation.clock import Clock, FrozenClock, SystemClock


class TestClockAbstraction:
    """Verify that Clock is an abstract base class."""

    def test_clock_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            Clock()  # type: ignore


class TestSystemClock:
    """Verify SystemClock returns real time values."""

    def setup_method(self):
        self.clock = SystemClock()

    def test_now_returns_datetime(self):
        result = self.clock.now()
        assert isinstance(result, datetime)

    def test_utcnow_returns_utc_datetime(self):
        result = self.clock.utcnow()
        assert isinstance(result, datetime)
        assert result.tzinfo is timezone.utc

    def test_timestamp_returns_float(self):
        result = self.clock.timestamp()
        assert isinstance(result, float)
        assert result > 0

    def test_utcnow_is_close_to_now(self):
        from time import time as system_time

        clock_ts = self.clock.timestamp()
        system_ts = system_time()
        # Allow 1 second difference for test execution
        assert abs(clock_ts - system_ts) < 1.0


class TestFrozenClock:
    """Verify FrozenClock returns the fixed time."""

    def test_default_construction_fixes_time(self):
        clock = FrozenClock()
        t1 = clock.now()
        t2 = clock.now()
        assert t1 == t2

    def test_frozen_datetime_provided(self):
        fixed = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        clock = FrozenClock(fixed)
        assert clock.now() == fixed
        assert clock.utcnow() == fixed

    def test_utcnow_without_tz(self):
        """When frozen datetime has no tzinfo, utcnow should add UTC."""
        fixed = datetime(2024, 6, 1, 0, 0, 0)
        clock = FrozenClock(fixed)
        utc_result = clock.utcnow()
        assert utc_result.tzinfo is timezone.utc

    def test_timestamp_consistency(self):
        fixed = datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        clock = FrozenClock(fixed)
        expected_ts = fixed.timestamp()
        assert clock.timestamp() == expected_ts

    def test_multiple_calls_return_same(self):
        fixed = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        clock = FrozenClock(fixed)
        assert clock.now() is clock.now()  # Same object reference (Final)

