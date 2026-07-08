"""
prompt_builder/exceptions.py

Domain exceptions raised by the Prompt Builder.
"""


class PromptBuilderError(Exception):
    """
    Base exception for all domain violations raised within the
    Prompt Builder package.
    """


class PromptValidationError(PromptBuilderError):
    """
    Raised when input, output, or final prompt token limit validation fails.
    """
