from sentence_transformers import CrossEncoder

model = None

def get_model():
    global model

    if model is None:
        model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )
        print("[RERANKER MODEL LOADED]")
    return model

def rerank(question, documents):

    pairs = [
    (question, doc.text)
    for doc in documents
    ]

    scores = get_model().predict(
    pairs
)

    ranked = sorted(
    zip(documents, scores),
    key=lambda x: x[1],
    reverse=True
)

    results = []

    for doc, score in ranked:
      doc.score = float(score)
      results.append(doc)

    return results