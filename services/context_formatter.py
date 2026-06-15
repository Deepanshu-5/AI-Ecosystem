from models.retrieved_chunk import RetrievedChunk


def format_context(
    chunks: list[RetrievedChunk]
) -> str:

    context_parts = []

    for i, chunk in enumerate(
        chunks,
        start=1
    ):

        context_parts.append(
            f"""
Source {i}

{chunk.text}
"""
        )

    return "\n".join(
        context_parts
    )