import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

import chromadb

from uuid import uuid4
from sentence_transformers import (
    SentenceTransformer
)

from config.settings import (
    CHROMA_PATH,
    EMBEDDING_MODEL
)

MEMORY_COLLECTION = "memory_base"

embedding_model = None

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

try:

    collection = client.get_collection(
        MEMORY_COLLECTION
    )

except:

    collection = client.create_collection(
        MEMORY_COLLECTION
    )


def get_embedding_model():

    global embedding_model

    if embedding_model is None:

        embedding_model = (
            SentenceTransformer(
                EMBEDDING_MODEL
            )
        )

    return embedding_model


def save_memory(
    content: str
):

    embedding = (
        get_embedding_model()
        .encode(content)
        .tolist()
    )

    collection.add(
        ids=[
            str(uuid4())
        ],
        documents=[
            content
        ],
        embeddings=[
            embedding
        ]
    )

    return True


def search_memory(
    query: str,
    top_k: int = 3
):

    query_embedding = (
    get_embedding_model()
    .encode(query)
    .tolist()
)

    results = collection.query(
    query_embeddings=[
        query_embedding
    ],
    n_results=top_k
)

    return {
    "documents": results["documents"][0],
    "distances": results["distances"][0]
}
def get_all_memories():

    return collection.get()

def delete_memory(
    memory_id: str
):

    collection.delete(
        ids=[memory_id]
    )

    return True

def delete_memories(
    ids: list[str]
):

    if not ids:
        return False

    collection.delete(
        ids=ids
    )

    return True

  