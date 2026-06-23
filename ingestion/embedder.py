from sentence_transformers import SentenceTransformer

from config.settings import EMBEDDING_MODEL

from shared.model_registry import (
    get_embedding_model
)

def get_model():
    return get_embedding_model(
        EMBEDDING_MODEL
    )


def create_embeddings(chunks: list[str]):

    embeddings = get_model().encode(chunks)

    return embeddings.tolist()