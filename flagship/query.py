"""
query.py - Ask questions against the indexed IT docs.
Connects to the same Chroma database that index_docs.py built,
retrieves the most relevant chunks, and sends them to Claude.
"""
import chromadb
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
anthropic_client = Anthropic()

# === 1. Connect to the SAME database index_docs.py wrote ===
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="maple_ai_docs")
print(f"Connected. Collection has {collection.count()} chunks.")

# === 2. Retrieve the most relevant chunks for a question ===
question = "When does my VPN expire?"

results = collection.query(
    query_texts=[question],
    n_results=3,
)
retrieved_chunks = results["documents"][0]
retrieved_metadata = results["metadatas"][0]

print(f"\n--- Retrieved {len(retrieved_chunks)} chunks for: '{question}' ---")
for i, (chunk, meta) in enumerate(zip(retrieved_chunks, retrieved_metadata), 1):
    print(f"\n[Chunk {i}] (from {meta['source']})")
    print(f"  {chunk}")

# === 3. Build a grounded prompt from the retrieved chunks ===
context = "\n\n---\n\n".join(retrieved_chunks)

prompt = f"""Answer the question using ONLY the information in the Context below.
If the Context does not contain the answer, say "I don't have that information in the provided documents."

Context:
{context}

Question: {question}

Answer:"""

# === 4. Send to Claude and print the grounded answer ===
print("\n--- Asking Claude... ---")
response = anthropic_client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=512,
    messages=[{"role": "user", "content": prompt}],
)

answer = response.content[0].text
print("\n--- ANSWER ---")
print(answer)