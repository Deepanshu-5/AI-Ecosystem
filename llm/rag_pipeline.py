from llm.rag import create_rag_prompt
from llm.base_generator import BaseGenerator


class RAGPipeline:

    def __init__(
        self,
        generator: BaseGenerator
    ):
        self.generator = generator

    def ask(
        self,
        question: str
    ) -> str:

        prompt = create_rag_prompt(
            question
        )

        return self.generator.generate(
            prompt
        )