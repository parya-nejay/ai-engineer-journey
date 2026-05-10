
import chromadb


# === 1. Read the document ===
print("Reading data.txt...")
with open("data.txt", "r", encoding="utf-8") as f:
    text = f.read()


# === 2. Split into chunks (one chunk per paragraph) ===
# Simple strategy: split on blank lines. Each paragraph becomes a chunk.
chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
print(f"Split document into {len(chunks)} chunks")


# === 3. Set up Chroma client (PersistentClient stores data on disk) ===
print("Setting up Chroma vector database...")
client = chromadb.PersistentClient(path="./chroma_db")

# Reset the collection on each run, so re-indexing gives clean results
#this code is basically saying:
#Delete the old saved data if it exists. If it doesn’t exist, ignore the error.”
try:
    client.delete_collection(name="maple_ai_docs")
except Exception:
    pass

# Create a fresh collection (like a "table" inside Chroma)
collection = client.create_collection(name="maple_ai_docs")

# === 4. Add chunks to the collection ===
# Chroma generates embeddings automatically using its built-in model.
# First run will download the embedding model (~80MB), which takes a minute.
print(f"Indexing {len(chunks)} chunks (first run doanloads embedding model)...")
collection.add(
    documents=chunks,
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)

# === 5. Verify ===
print(f"\nDone. Collection now contains {collection.count()} chunks.")
print(f"Vector database stored at: ./chroma_db/")

