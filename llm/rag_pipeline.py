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
        question: str,
        session_id: str = ""
    ) -> str:

        return create_rag_prompt(
            question,
            session_id=session_id
        )