import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

import chromadb

from config.settings import (
    CHROMA_PATH
)

MEMORY_COLLECTION = "memory_base"

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    MEMORY_COLLECTION
)


def deduplicate():

    data = collection.get()
    print("Before:", len(data["documents"]))

    ids = data["ids"]
    documents = data["documents"]

    seen = set()

    duplicate_ids = []

    for doc_id, doc in zip(
        ids,
        documents
    ):

        normalized = (
            doc.strip().lower()
        )

        if normalized in seen:

            duplicate_ids.append(
                doc_id
            )

        else:

            seen.add(
                normalized
            )

    if duplicate_ids:

        collection.delete(
            ids=duplicate_ids
        )

    print("After:", collection.count())
    print(
        f"Removed {len(duplicate_ids)} duplicates"
    )


if __name__ == "__main__":

    deduplicate()