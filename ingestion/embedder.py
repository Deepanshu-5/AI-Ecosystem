from sentence_transformers import SentenceTransformer

from config.settings import EMBEDDING_MODEL

model = SentenceTransformer(EMBEDDING_MODEL)


def create_embeddings(chunks: list[str]):

    embeddings = model.encode(chunks)

    return embeddings.tolist()