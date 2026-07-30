"""
fusion.py - pure ranking math. No disk, no network, no models.
Separated from retrieval.py so it can be tested without building an index.
"""


def rrf_fuse(vec_ids, kw_ids, top_k, k=60):
    """Merge two ranked ID lists by Reciprocal Rank Fusion.

    Only rank POSITION matters, not the original scores - that's why RRF can
    fuse vector distances and BM25 scores, which are on different scales.
    """
    scores = {}
    for ranked in (vec_ids, kw_ids):
        for rank, cid in enumerate(ranked):
            scores[cid] = scores.get(cid, 0) + 1.0 / (k + rank + 1)
    return sorted(scores, key=lambda cid: scores[cid], reverse=True)[:top_k]