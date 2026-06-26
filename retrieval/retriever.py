import chromadb
from sentence_transformers import SentenceTransformer
from config.settings import (
    CHROMA_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL
)

model = None
client = None
collection = None
from shared.model_registry import (
    get_embedding_model
)



from dataclasses import dataclass, field

@dataclass
class Document:
    text: str
    metadata: dict = field(default_factory=dict)
    score: float = 0.0


def get_model():
    global model
    if model is None:
        model = get_embedding_model( EMBEDDING_MODEL)
        print("[EMBEDDING MODEL LOADED]")
    return model


def get_collection():
    global client, collection
    if collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_collection(COLLECTION_NAME)
    return collection


def retrieve(query, top_k=5):
    embedding = get_model().encode(query).tolist()

    results = get_collection().query(
        query_embeddings=[embedding],
        n_results=top_k
    )

    documents = []
    for text, metadata in zip(
        results["documents"][0],
        results["metadatas"][0]
    ):
        documents.append(Document(text=text, metadata=metadata))

    return documents