"""
Smoke test — does source_filter actually scope vector_search?
Same question, two queries: without filter, then with filter.
"""
from retrieval import vector_search

question = "Who is the CEO?"

print("=" * 60)
print("WITHOUT FILTER (searches all 684 chunks):")
print("=" * 60)
chunks, metadatas = vector_search(question, top_k=3)
for i, (chunk, meta) in enumerate(zip(chunks, metadatas), 1):
    print(f"\n[{i}] source = {meta.get('source')}")
    print(f"    {chunk[:120]}...")

print("\n" + "=" * 60)
print("WITH FILTER source='data.txt' (Maple AI only):")
print("=" * 60)
chunks, metadatas = vector_search(question, top_k=3, source_filter="data.txt")
for i, (chunk, meta) in enumerate(zip(chunks, metadatas), 1):
    print(f"\n[{i}] source = {meta.get('source')}")
    print(f"    {chunk[:120]}...")