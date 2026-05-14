"""
RAG Evaluation Script.

Runs the eval dataset against the RAG system and produces a quality report.
"""

from anthropic import Anthropic
from dotenv import load_dotenv
from eval_dataset import EVAL_DATASET
from retrieval import hybrid_search    # ← NEW: import our hybrid search

load_dotenv()
anthropic_client = Anthropic()

# chroma_client = chromadb.PersistentClient(path="./chroma_db")
# collection = chroma_client.get_collection(name="maple_ai_docs")


# def rag_answer(question: str, top_k: int = 3) -> str:
#     """Run a single question through the RAG pipeline. Returns the answer string."""
#     # 1. Retrieve
#     results = collection.query(query_texts=[question], n_results=top_k)
#     retrieved_chunks = results["documents"][0]
#     retrieved_metadata = results["metadatas"][0]

def rag_answer(question: str, top_k: int = 3) -> str:
    """Run a single question through the RAG pipeline. Returns the answer string."""
    # # 1. Retrieve (HYBRID search: vector + keyword combined)
    # retrieved_chunks, retrieved_metadata = hybrid_search(question, top_k=top_k)
    # 1. Retrieve (HYBRID search: vector + keyword combined, scoped to Maple AI docs)
    retrieved_chunks, retrieved_metadata = hybrid_search(question, top_k=top_k, source_filter="data.txt")

    # 2. Build numbered context
    context_parts = []
    for i, (chunk, meta) in enumerate(zip(retrieved_chunks, retrieved_metadata), 1):
        context_parts.append(
            f"[Chunk {i}] (source: {meta['source']}, position {meta['chunk_index']}/{meta['total_chunks']})\n{chunk}"
        )
    context = "\n\n---\n\n".join(context_parts)

    # 3. Build prompt
    prompt = f"""Answer the question using ONLY the information in the Context below.
Each Context section is numbered: [Chunk 1], [Chunk 2], etc.
When you use information from a Context section, cite it inline like this: [Source: Chunk 1].
If the Context does not contain the answer, say "I don't have that information in the provided documents."

Context:
{context}

Question: {question}

Answer (with inline citations):"""

    # 4. Call Claude
    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def evaluate_answer(test_case: dict, answer: str) -> dict:
    """Score a single answer against expected facts / refusal."""

    # Phrases that indicate a refusal
    refusal_phrases = [
        "don't have", "do not have", "not in the provided",
        "not in the documents", "no information", "doesn't contain", "does not contain"
    ]
    detected_refusal = any(phrase in answer.lower() for phrase in refusal_phrases)

    # Case 1: Question SHOULD be refused
    if test_case["expected_refusal"]:
        passed = detected_refusal
        return {
            "passed": passed,
            "reason": "Correctly refused" if passed else "FAILED to refuse - possible hallucination",
        }

    # Case 2: Question should NOT be refused, but system refused anyway
    if detected_refusal:
        return {
            "passed": False,
            "reason": "Incorrectly refused - the answer IS in the documents",
        }

    # Case 3: Check that expected facts appear in the answer
    found = []
    missing = []
    for fact in test_case["expected_facts"]:
        if fact.lower() in answer.lower():
            found.append(fact)
        else:
            missing.append(fact)

    fact_coverage = len(found) / len(test_case["expected_facts"]) if test_case["expected_facts"] else 1.0
    # Need >= 50% of expected facts to pass
    passed = fact_coverage >= 0.5

    if passed and missing:
        reason = f"Found {len(found)}/{len(test_case['expected_facts'])} facts (missing: {missing})"
    elif passed:
        reason = f"Found all {len(found)} expected facts"
    else:
        reason = f"Only {len(found)}/{len(test_case['expected_facts'])} facts found (missing: {missing})"

    return {"passed": passed, "reason": reason}


def main():
    print("=" * 70)
    print("RAG EVALUATION REPORT")
    print("=" * 70)

    results = []

    for tc in EVAL_DATASET:
        print(f"\n--- [{tc['id']}] ({tc['difficulty']}): {tc['question']}")

        answer = rag_answer(tc["question"])
        preview = answer[:250] + "..." if len(answer) > 250 else answer
        print(f"Answer: {preview}")

        score = evaluate_answer(tc, answer)
        status = "PASS" if score["passed"] else "FAIL"
        print(f"[{status}] {score['reason']}")

        results.append({
            "id": tc["id"],
            "difficulty": tc["difficulty"],
            "passed": score["passed"],
            "reason": score["reason"],
        })

    # === Summary ===
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print(f"\nOverall: {passed}/{total} passed ({100*passed/total:.0f}%)")

    for diff in ["easy", "medium", "hard"]:
        diff_results = [r for r in results if r["difficulty"] == diff]
        if not diff_results:
            continue
        diff_total = len(diff_results)
        diff_passed = sum(1 for r in diff_results if r["passed"])
        print(f"  {diff.capitalize():8s}: {diff_passed}/{diff_total}")

    # List failed tests
    failed = [r for r in results if not r["passed"]]
    if failed:
        print(f"\nFailed tests ({len(failed)}):")
        for r in failed:
            print(f"  [{r['id']}] {r['reason']}")
    else:
        print("\nAll tests passed!")


if __name__ == "__main__":
    main()
