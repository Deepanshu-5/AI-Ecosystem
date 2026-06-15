import sys
from pathlib import Path

root = str(Path(__file__).resolve().parent.parent)

if root not in sys.path:
    sys.path.insert(0, root)

import chromadb
from ingestion.extractor import extract_document
from ingestion.chunker import create_chunks
from ingestion.embedder import create_embeddings

from config.settings import (
    CHROMA_PATH,
    COLLECTION_NAME
)


def main():

    text = extract_document("data/raw/Python Interview Questions.pdf")

    chunks = create_chunks(text)

    embeddings = create_embeddings(chunks)

    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )
 
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = [
        f"chunk_{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            "source": "Python Interview Questions.pdf",
            "chunk": i
        }
        for i in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(
        f"Stored {len(chunks)} chunks in ChromaDB"
    )

    print(
        f"Collection Size: {collection.count()}"
    )
    
    print(f"Total Chunks: {len(chunks)}")

if __name__ == "__main__":
    main()