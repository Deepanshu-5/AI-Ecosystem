"""
Tests for platform/foundation/id_generator.py

Verifies IdGenerator abstraction and UuidGenerator implementation.
"""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[3])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
import uuid as uuid_mod

from platcore.foundation.id_generator import IdGenerator, UuidGenerator


class TestIdGeneratorAbstraction:
    """Verify that IdGenerator is an abstract base class."""

    def test_id_generator_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            IdGenerator()  # type: ignore


class TestUuidGenerator:
    """Verify UuidGenerator produces valid UUID4 strings."""

    def setup_method(self):
        self.generator = UuidGenerator()

    def test_generate_returns_string(self):
        result = self.generator.generate()
        assert isinstance(result, str)

    def test_generate_returns_valid_uuid4(self):
        result = self.generator.generate()
        # Verify it's a valid UUID by parsing it
        parsed = uuid_mod.UUID(result)
        assert parsed.version == 4

    def test_generates_unique_ids(self):
        ids = {self.generator.generate() for _ in range(1000)}
        assert len(ids) == 1000  # All unique

    def test_generated_id_format(self):
        result = self.generator.generate()
        # Standard UUID format: 8-4-4-4-12 hex digits
        parts = result.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

