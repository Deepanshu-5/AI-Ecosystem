import re


def create_chunks(text: str) -> list[str]:

    pattern = r"(Q\d+.*?)(?=Q\d+|$)"

    chunks = re.findall(
        pattern,
        text,
        flags=re.DOTALL
    )

    return [
        chunk.strip()
        for chunk in chunks
    ]