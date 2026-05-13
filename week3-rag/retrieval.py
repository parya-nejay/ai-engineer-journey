"""
retrieval.py — search strategies for RAG.

Provides three search functions:
- vector_search()  : semantic similarity (Chroma's built-in embeddings)
- keyword_search() : BM25 keyword matching
- hybrid_search()  : combines both via Reciprocal Rank Fusion (RRF)
"""

import chromadb
from rank_bm25 import BM25Okapi


# === Connect to Chroma ===
_chroma_client = chromadb.PersistentClient(path="./chroma_db")
_collection = _chroma_client.get_collection(name="maple_ai_docs")


# === Load all chunks once and build BM25 index ===
print("Building BM25 keyword index...")
_all_data = _collection.get()
_ALL_CHUNKS = _all_data["documents"]
_ALL_IDS = _all_data["ids"]
_ALL_METADATA = _all_data["metadatas"]

# Map chunk_id -> position in lists (for fast lookups later)
_id_to_index = {chunk_id: i for i, chunk_id in enumerate(_ALL_IDS)}

# Tokenize each chunk into lowercased words for BM25
_tokenized_corpus = [chunk.lower().split() for chunk in _ALL_CHUNKS]
_bm25 = BM25Okapi(_tokenized_corpus)
print(f"  BM25 index ready with {len(_ALL_CHUNKS)} chunks")


def vector_search(question: str, top_k: int = 3):
    """Pure semantic search via Chroma."""
    results = _collection.query(query_texts=[question], n_results=top_k)
    return results["documents"][0], results["metadatas"][0]


def keyword_search(question: str, top_k: int = 3):
    """Pure keyword search via BM25."""
    tokenized_query = question.lower().split()
    scores = _bm25.get_scores(tokenized_query)

    # Get the indices of the top_k highest-scoring chunks
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

    chunks = [_ALL_CHUNKS[i] for i in top_indices]
    metadatas = [_ALL_METADATA[i] for i in top_indices]
    return chunks, metadatas


def hybrid_search(question: str, top_k: int = 3, candidates_per_method: int = 6):
    """
    Hybrid search: combine vector + keyword search using Reciprocal Rank Fusion.

    Args:
        question: the user's question
        top_k: how many final chunks to return
        candidates_per_method: how many chunks each method contributes before fusion
    """
    # 1. Vector search → get IDs ranked by semantic similarity
    vec_results = _collection.query(
        query_texts=[question], n_results=candidates_per_method
    )
    vec_ids = vec_results["ids"][0]

    # 2. Keyword search → get IDs ranked by BM25 score
    tokenized_query = question.lower().split()
    scores = _bm25.get_scores(tokenized_query)
    keyword_top_indices = sorted(
        range(len(scores)), key=lambda i: scores[i], reverse=True
    )[:candidates_per_method]
    keyword_ids = [_ALL_IDS[i] for i in keyword_top_indices]

    # 3. Reciprocal Rank Fusion (RRF): combine the rankings
    # Formula: score(chunk) = sum over methods of 1 / (k + rank)
    # k=60 is the standard constant from the RRF paper
    rrf_scores = {}
    rrf_k = 60

    for rank, chunk_id in enumerate(vec_ids):
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1.0 / (rrf_k + rank + 1)

    for rank, chunk_id in enumerate(keyword_ids):
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1.0 / (rrf_k + rank + 1)

    # 4. Sort chunks by combined score and take top_k
    sorted_ids = sorted(
        rrf_scores.keys(), key=lambda chunk_id: rrf_scores[chunk_id], reverse=True
    )[:top_k]

    # 5. Fetch the actual chunk text + metadata
    chunks = [_ALL_CHUNKS[_id_to_index[chunk_id]] for chunk_id in sorted_ids]
    metadatas = [_ALL_METADATA[_id_to_index[chunk_id]] for chunk_id in sorted_ids]
    return chunks, metadatas
