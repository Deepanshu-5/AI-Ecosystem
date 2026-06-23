from services.context_service import build_context
from models.retrieved_chunk import RetrievedChunk

def format_context(chunks: list[RetrievedChunk]) -> str:
    # Convert RetrievedChunk to the Document-like object expected by build_context
    class _Doc:
        def __init__(self, text, metadata):
            self.text = text
            self.metadata = metadata

    docs = [
    _Doc(
        c.text,
        c.metadata
    )
    for c in chunks
]
    return build_context(docs)