from retrieval import hybrid_search, rerank
from agent_demo import run_agent  # your Day 16 loop — adapt import if needed

# --- Tool executor ---
def search_company_docs(query: str) -> str:
    candidate_chunks, candidate_metadata = hybrid_search(
        query, top_k=10, candidates_per_method=10
    )
    retrieved_chunks, retrieved_metadata = rerank(
        query, candidate_chunks, candidate_metadata, top_k=3
    )
    context_parts = []
    for i, (chunk, meta) in enumerate(zip(retrieved_chunks, retrieved_metadata), 1):
        context_parts.append(
            f"[Chunk {i}] (source: {meta['source']}, position {meta['chunk_index']}/{meta['total_chunks']})\n{chunk}"
        )
    return "\n\n---\n\n".join(context_parts)

# --- Tool declaration ---
SEARCH_TOOL = {
    "name": "search_company_docs",
    "description": (
        "Searches the Maple AI company knowledge base for information about "
        "Maple AI's products, pricing, refund policy, customer support, "
        "company leadership and history, office locations, and the employee "
        "handbook. Also contains general reference information about the "
        "city of Toronto. Use this whenever a question asks about Maple AI "
        "or any of the topics listed above."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A focused search query — the specific topic or question to look up, not the user's full message verbatim."
            }
        },
        "required": ["query"]
    }
}

# --- Wire it up ---
TOOLS = [SEARCH_TOOL]
TOOL_FUNCTIONS = {
    # "search_company_docs": lambda input: search_company_docs(input["query"]),
    "search_company_docs": search_company_docs,
}

# --- The two-test proof of the inversion ---
if __name__ == "__main__":
    tests = [
        "What is 2 + 2?",                       # expect: no tool, direct answer
        "What's Maple AI's refund policy?",     # expect: tool_use → retrieval → answer
        "What is the population of Toronto?",   # gray zone: tool description claims Toronto coverage, but Claude knows Toronto from training
    ]
    for q in tests:
        print(f"\n{'='*60}\nQ: {q}\n{'='*60}")
        answer = run_agent(q, TOOLS, TOOL_FUNCTIONS)
        print(f"\nA: {answer}")