from retrieval.retriever import Document

def build_context(
    chunks: list[Document]
) -> str:

    context_parts = []

    for i, chunk in enumerate(
        chunks,
        start=1
    ):

        source = chunk.metadata.get(
            "source",
            "Unknown"
        )

        context_parts.append(
            f"""
Source {i}
File: {source}

{chunk.text}
"""
        )

    return "\n".join(
        context_parts
    )