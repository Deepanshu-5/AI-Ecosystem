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

    collection.add(
        ids=[
            str(uuid4())
        ],
        documents=[
            content
        ]
    )

    return True


def search_memory(
    query: str,
    top_k: int = 3
):

    results = collection.query(
    query_texts=[
        query
    ],
    n_results=top_k
)

    return results["documents"][0]


if __name__ == "__main__":

    save_memory(
        "User integrated Claude Desktop MCP successfully."
    )

    memories = search_memory(
        "Claude MCP"
    )

    print(
        memories
    )
    print(
    collection.count()
)