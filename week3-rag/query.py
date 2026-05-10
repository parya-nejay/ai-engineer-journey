"""
Day 7 - RAG query script.

Takes a user question, retrieves relevant chunks from Chroma,
and asks Claude to answer based on those chunks.
"""
import chromadb
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
anthropic_client = Anthropic()
client = chromadb.PersistentClient(
    path="./chroma_db")  # CONNECT TO CHROMA DATABASE

collection = client.get_collection(name="maple_ai_docs")


def ask(question: str, top_k: int = 3):
    """Ask a question and get an answer grounded in the indexed documents."""
    # === 2. Retrieve relevant chunks from Chroma ===
    # Chroma converts the question to an embedding internally
    # and finds the most similar chunks.
    results = collection.query(query_texts=[question], n_results=top_k,)
    retrieved_chunks = results['documents'][0]

    # Show what was retrieved (great for debugging RAG)
    print(f"\n--- Retrieved {len(retrieved_chunks)} chunks from Chroma ---")
    for i, chunk in enumerate(retrieved_chunks, 1):
        preview = chunk[:150] + "..." if len(chunk) > 150 else chunk
        print(f"[Chunk {i}] {preview}")

    # === 3. Build a prompt that includes the retrieved chunks ===
    context = "\n\n---\n\n".join(retrieved_chunks)

    prompt = f"""Answer the question using ONLY the information in the Context below.
If the Context does not contain the answer, say "I don't have that information in the provided documents."

Context:
{context}

Question: {question}

Answer:"""

    # === 4. Send to Claude ===
    print("\n--- Asking Claude... ---")
    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.content[0].text
    print("\n--- ANSWER ---")
    print(answer)
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Maple AI Knowledge Base - ask me anything!")
    print("Type 'quit' to exit.")
    print()
    print("Example questions to try:")
    print("  - What is the refund policy?")
    print("  - How much does the Professional tier cost?")
    print("  - Who founded the company?")
    print("  - What is the company stock price?")
    print("    (NOT in the doc - watch what happens!)")
    print("=" * 60)

    while True:
        question = input("\nYour question> ").strip()
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if not question:
            continue
        try:
            ask(question)
        except Exception as e:
            print(f"Error: {e}")
