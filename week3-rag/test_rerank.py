from sentence_transformers import CrossEncoder

# Load the cross-encoder
# First run downloads the model (~80MB) — it gets cached after that
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

query = "Who is the CEO of Maple AI?"

chunk_a = "Maple AI's founder, Jane Doe, started the company in 2018."
chunk_b = "ACME Corp's CEO Tim Smith spoke at the conference last year."

# predict() takes a list of (query, chunk) pairs and returns a score per pair
scores = model.predict([
    (query, chunk_a),
    (query, chunk_b),
])

print(f"Query: {query}\n")
print(f"Chunk A score: {scores[0]:.4f}")
print(f"  -> {chunk_a}\n")
print(f"Chunk B score: {scores[1]:.4f}")
print(f"  -> {chunk_b}")