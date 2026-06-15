# search_knowledge.py

from services.knowledge_service import search


def search_knowledge(
    question: str
):
    chunks = search(
        question
    )

    return "\n\n".join(
        chunk.text          # ✅ chunk is already a string
        for chunk in chunks
    )