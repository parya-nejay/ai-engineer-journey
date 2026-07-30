from fusion import rrf_fuse


def test_consensus_beats_a_single_strong_pick():
    """A chunk both methods found should outrank one only vector found.
    This is exactly WHY hybrid lost the Day 33 A/B at top_k=1."""
    vec_ids = ["a", "b"]
    kw_ids = ["b", "c"]
    assert rrf_fuse(vec_ids, kw_ids, top_k=1) == ["b"]


def test_top_k_limits_the_result():
    assert len(rrf_fuse(["a", "b", "c"], ["d", "e"], top_k=2)) == 2


def test_empty_keyword_list_preserves_vector_order():
    """mode='vector' passes kw_ids=[] instead of using a second code path.
    This test is the proof that shortcut is safe."""
    assert rrf_fuse(["a", "b", "c"], [], top_k=3) == ["a", "b", "c"]