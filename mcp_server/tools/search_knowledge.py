from services.knowledge_service import search
from services.context_service import build_context

def search_knowledge(
    question: str
):

    chunks = search(
        question
    )

    return build_context(
        chunks
    )