"""
platform/foundation/id_generator.py

Identifier generation abstraction and default implementation.

Provides a provider-agnostic IdGenerator interface that decouples
identifier creation from any specific algorithm.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod


class IdGenerator(ABC):
    """
    Abstract identifier generator.

    Responsibility:
        Generate unique identifiers for platform entities (sessions,
        requests, resources, etc.).

    This is a stable public contract. Consumers depend on this abstraction,
    not on any concrete implementation.
    """

    @abstractmethod
    def generate(self) -> str:
        """
        Generate a unique identifier.

        Returns:
            A ``str`` representing a unique identifier. The format and
            algorithm are implementation-specific.
        """


class UuidGenerator(IdGenerator):
    """
    Concrete identifier generator using UUID v4.

    This is the default production implementation. It generates UUID4
    strings (standard hexadecimal format with dashes).

    This class is part of the internal implementation, not the public
    contract. Consumers should depend on ``IdGenerator``.
    """

    def generate(self) -> str:
        return str(uuid.uuid4())
