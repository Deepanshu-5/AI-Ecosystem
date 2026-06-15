from retrieval.retriever import retrieve
from retrieval.reranker import rerank
from services.cache_service import cache

from config.settings import (
    FINAL_CONTEXT_CHUNKS,
    MIN_RERANK_SCORE,
    RERANK_TOP_K
)

def search(
    question: str,
    top_k: int = RERANK_TOP_K,
    final_k: int = FINAL_CONTEXT_CHUNKS
):
    cached_result = cache.get(question)
    if cached_result:
     print("CACHE HIT")
     return cached_result
 
    results = retrieve(
        question,
        top_k
    )

    ranked = rerank(
        question,
        results
    )
    best_chunks = []

    for chunk in ranked:

      if chunk.score > MIN_RERANK_SCORE:
        best_chunks.append(chunk)

      if len(best_chunks) >= final_k:
        break

    result = (
    best_chunks
    if best_chunks
    else ranked[:final_k]
)

    cache.set(
    question,
    result
)

    return result

 