import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

import chromadb
from uuid import uuid4
from sentence_transformers import SentenceTransformer

from config.settings import (
    CHROMA_PATH,
    EMBEDDING_MODEL
)

MEMORY_COLLECTION = "memory_base"

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

old_collection = client.get_collection(
    MEMORY_COLLECTION
)

data = old_collection.get()

documents = data["documents"]

print(
    f"Exported {len(documents)} memories"
)

client.delete_collection(
    MEMORY_COLLECTION
)

new_collection = client.create_collection(
    MEMORY_COLLECTION
)

model = SentenceTransformer(
    EMBEDDING_MODEL
)

for doc in documents:

    embedding = (
        model.encode(doc)
        .tolist()
    )

    new_collection.add(
        ids=[
            str(uuid4())
        ],
        documents=[
            doc
        ],
        embeddings=[
            embedding
        ]
    )

print(
    f"Rebuilt collection with {new_collection.count()} memories"
)