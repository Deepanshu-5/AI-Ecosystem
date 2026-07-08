"""
tests/prompt_builder/test_prompt.py

Unit tests for Prompt.
"""

from __future__ import annotations

import pytest

from prompt_builder.prompt import CURRENT_SCHEMA_VERSION, Prompt


class TestPrompt:
    def test_creation(self) -> None:
        prompt = Prompt(content="[QUERY]\nhello")
        assert prompt.content == "[QUERY]\nhello"
        assert prompt.version == CURRENT_SCHEMA_VERSION

    def test_explicit_version(self) -> None:
        prompt = Prompt(content="[QUERY]\nhello", version=1)
        assert prompt.version == 1

    def test_immutability(self) -> None:
        prompt = Prompt(content="[QUERY]\nhello")
        with pytest.raises(AttributeError):
            prompt.content = "changed"  # type: ignore[misc]

    def test_default_schema_version(self) -> None:
        prompt = Prompt(content="[QUERY]\nhello")
        assert prompt.version == 1

    def test_to_dict(self) -> None:
        prompt = Prompt(content="[QUERY]\nhello")
        d = prompt.to_dict()
        assert d == {"content": "[QUERY]\nhello", "version": 1}

    def test_to_dict_key_order(self) -> None:
        prompt = Prompt(content="[QUERY]\nhello")
        assert list(prompt.to_dict().keys()) == ["content", "version"]

    def test_to_dict_stable(self) -> None:
        prompt = Prompt(content="[QUERY]\nhello")
        assert prompt.to_dict() == prompt.to_dict()
