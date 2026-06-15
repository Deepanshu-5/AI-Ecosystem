from llm.placeholder_generator import (
    PlaceholderGenerator
)

from llm.ollama_generator import (
    OllamaGenerator
)


class GeneratorFactory:

    @staticmethod
    def create(
        provider: str = "placeholder"
    ):

        if provider == "ollama":
           return OllamaGenerator()

        return OllamaGenerator()