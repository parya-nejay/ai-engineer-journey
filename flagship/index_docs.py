"""
index_docs.py - Build the Chroma vector database from ALL documents in docs/

This script:
1. Uses load_documents() to read every file in the docs/ folder (.txt + .pdf)
2. Splits each document into chunks with smart paragraph-aware splitting
3. Stores chunks in Chroma with metadata showing the source filename
"""

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

from loader import load_documents


# === 1. Load all documents from the docs/ folder ===
print("Loading documents from docs/...")
documents = load_documents("docs")
print(f"Loaded {len(documents)} document(s)")


# === 2. Split each document into chunks (keeping track of source) ===
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""],
)

all_chunks = []
all_metadatas = []
all_ids = []

for doc in documents:
    source = doc["source"]
    chunks = splitter.split_text(doc["text"])
    print(f"  '{source}' → {len(chunks)} chunks")

    for i, chunk in enumerate(chunks):
        all_chunks.append(chunk)
        all_metadatas.append({
            "source": source,
            "chunk_index": i,
            "total_chunks": len(chunks),
        })
        # ID prefixed with source so chunk_0 from handbook.txt
        # doesn't collide with chunk_0 from product_faq.txt
        all_ids.append(f"{source}__chunk_{i}")

print(f"\nTotal chunks across all documents: {len(all_chunks)}")


# === 3. Set up Chroma ===
print("\nSetting up Chroma vector database...")
client = chromadb.PersistentClient(path="./chroma_db")

try:
    client.delete_collection(name="maple_ai_docs")
except Exception:
    pass

collection = client.create_collection(name="maple_ai_docs")


# === 4. Add all chunks to the collection ===
print(f"Indexing {len(all_chunks)} chunks...")
collection.add(
    documents=all_chunks,
    ids=all_ids,
    metadatas=all_metadatas,
)


# === 5. Verify ===
print(f"\n✅ Done. Collection now contains {collection.count()} chunks.")
print(f"Vector database stored at: ./chroma_db/")


# import chromadb
# from langchain_text_splitters import RecursiveCharacterTextSplitter


# # === 1. Read the document ===
# print("Reading data.txt...")
# with open("data.txt", "r", encoding="utf-8") as f:
#     # text = f.read()


# # === 2. Split into chunks (one chunk per paragraph) ===
# # Simple strategy: split on blank lines. Each paragraph becomes a chunk.
# # chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
# # print(f"Split document into {len(chunks)} chunks")

# # NEW
# # === 2. Split into chunks using a smart recursive splitter ===
# # RecursiveCharacterTextSplitter tries to split on:
# #   1. Paragraph breaks (\n\n)
# #   2. Then line breaks (\n)
# #   3. Then sentence ends (. )
# #   4. Then spaces
# #   5. Then characters (last resort)
# # This preserves semantic boundaries where possible.

# splitter = RecursiveCharacterTextSplitter(
#     chunk_size=500,
#     chunk_overlap=50,
#     separators=["\n\n", "\n", ". ", " ", ""],
# )
# chunks = splitter.split_text(text)
# print(f"Split document into {len(chunks)} chunks")


# # === 3. Set up Chroma client (PersistentClient stores data on disk) ===
# print("Setting up Chroma vector database...")
# client = chromadb.PersistentClient(path="./chroma_db")

# # Reset the collection on each run, so re-indexing gives clean results
# # this code is basically saying:
# # Delete the old saved data if it exists. If it doesn’t exist, ignore the error.”
# try:
#     client.delete_collection(name="maple_ai_docs")
# except Exception:
#     pass

# # Create a fresh collection (like a "table" inside Chroma)
# collection = client.create_collection(name="maple_ai_docs")

# # === 4. Add chunks to the collection ===
# # Chroma generates embeddings automatically using its built-in model.
# # First run will download the embedding model (~80MB), which takes a minute.
# print(
#     f"Indexing {len(chunks)} chunks (first run doanloads embedding model)...")
# # collection.add(
# #     documents=chunks,
# #     ids=[f"chunk_{i}" for i in range(len(chunks))]
# # )

# metadatas = [
#     {
#         "source": "data.txt",
#         "chunk_index": i,
#         "total_chunks": len(chunks)
#     }
#     for i in range(len(chunks))
# ]
# collection.add(
#     documents=chunks,
#     ids=[f"chunk_{i}" for i in range(len(chunks))],
#     metadatas=metadatas,
# )

# # === 5. Verify ===
# print(f"\nDone. Collection now contains {collection.count()} chunks.")
# print(f"Vector database stored at: ./chroma_db/")
