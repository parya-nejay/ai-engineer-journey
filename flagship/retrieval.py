"""
retrieval.py — search strategies for the flagship RAG.
vector + BM25 + Reciprocal Rank Fusion (RRF).
"""
import time
import logging
import chromadb
from rank_bm25 import BM25Okapi

log = logging.getLogger("flagship")

_client = chromadb.PersistentClient(path="./chroma_db")
_collection = _client.get_collection(name="maple_ai_docs")

# Load all chunks once, build BM25 index
_data = _collection.get()
_ALL_CHUNKS = _data["documents"]
_ALL_IDS = _data["ids"]
_ALL_METADATA = _data["metadatas"]
_id_to_index = {cid: i for i, cid in enumerate(_ALL_IDS)}

_tokenized_corpus = [c.lower().split() for c in _ALL_CHUNKS]
_bm25 = BM25Okapi(_tokenized_corpus)
print(f"BM25 index ready with {len(_ALL_CHUNKS)} chunks")


def hybrid_search(question, top_k=3, candidates_per_method=6, mode="hybrid"):
    # 1. Vector search → ranked IDs
    t_vec = time.perf_counter()
    vec = _collection.query(query_texts=[question], n_results=candidates_per_method)
    vec_ids = vec["ids"][0]
    vec_ms = (time.perf_counter() - t_vec) * 1000

    t_rest = time.perf_counter()

    # 2. BM25 keyword search → ranked IDs
    kw_ids = []
    if mode == "hybrid":
        scores = _bm25.get_scores(question.lower().split())
        kw_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:candidates_per_method]
        kw_ids = [_ALL_IDS[i] for i in kw_indices]

    # 3. Reciprocal Rank Fusion
    rrf, k = {}, 60
    for rank, cid in enumerate(vec_ids):
        rrf[cid] = rrf.get(cid, 0) + 1.0 / (k + rank + 1)
    for rank, cid in enumerate(kw_ids):
        rrf[cid] = rrf.get(cid, 0) + 1.0 / (k + rank + 1)

    # 4. Top_k by fused score
    top_ids = sorted(rrf, key=lambda cid: rrf[cid], reverse=True)[:top_k]
    chunks = [_ALL_CHUNKS[_id_to_index[cid]] for cid in top_ids]
    metas = [_ALL_METADATA[_id_to_index[cid]] for cid in top_ids]
    rest_ms = (time.perf_counter() - t_rest) * 1000

    log.info(f"[retrieval] vector_ms={vec_ms:.0f} rest_ms={rest_ms:.0f}")
    return chunks, metas