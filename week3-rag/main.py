"""
Day 9 - RAG as a FastAPI endpoint.

Exposes the RAG system as a web API. Uses the Chroma collection
already built by index_docs.py.
"""

import logging
import anthropic
import chromadb
from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# === Logging configuration ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)
logger = logging.getLogger(__name__)
# Python logging is used to track application events, errors, warnings, and debugging information.
# basicConfig() sets global logging behavior like format and level.
# getLogger(__name__) creates a logger specific to the current module.

# === Load env and initialize clients ONCE at startup ===
load_dotenv()

logger.info("Initializing clients...")
anthropic_client = Anthropic()
chroma_client = chromadb.PersistentClient(path="./chroma_db") #Connect to a vector database, ChromaDB stores embeddings/vectors for AI search
collection = chroma_client.get_collection(name="maple_ai_docs") #Open a table/container of vectors - open stored embedding
logger.info(f"Ready - {collection.count()} chunks loaded from Chroma")

# === FastAPI app ===
app = FastAPI(title="Maple AI RAG Service") #This initializes the backend application.

# === Pydantic models for request and response ===
class RAGRequest(BaseModel):
    question: str
    top_k: int = 3   # number of chunks to retrieve (default 3)


class RetrievedChunk(BaseModel):
    text: str
    source: str
    chunk_index: int


class RAGResponse(BaseModel):
    question: str
    answer: str
    retrieved_chunks: list[RetrievedChunk]
    input_tokens: int
    output_tokens: int
    
    # === Endpoints ===

@app.get("/")
def root():
    """Health check + show how many chunks are indexed."""
    return {
        "message": "RAG service is running",
        "chunks_indexed": collection.count(),
    }


@app.post("/rag-chat", response_model=RAGResponse)
def rag_chat(request: RAGRequest):
    """Answer a question using RAG: retrieve relevant chunks, then ask Claude."""

    logger.info(f"/rag-chat received question ({len(request.question)} chars, top_k={request.top_k})")

    try:
        # 1. Retrieve relevant chunks with metadata (It searches the vector database for the most semantically similar chunks to the user’s question and returns the top results)
        results = collection.query(
            query_texts=[request.question],
            n_results=request.top_k,
        )
        retrieved_chunks = results["documents"][0]
        retrieved_metadata = results["metadatas"][0]

        # 2. Build numbered context for citations
        context_parts = []
        for i, (chunk, meta) in enumerate(zip(retrieved_chunks, retrieved_metadata), 1):
            context_parts.append(
                f"[Chunk {i}] (source: {meta['source']}, position {meta['chunk_index']}/{meta['total_chunks']})\n{chunk}"
            )
        context = "\n\n---\n\n".join(context_parts)

# 3. Build the RAG prompt
        prompt = f"""Answer the question using ONLY the information in the Context below.
Each Context section is numbered: [Chunk 1], [Chunk 2], etc.
When you use information from a Context section, cite it inline like this: [Source: Chunk 1].
If the Context does not contain the answer, say "I don't have that information in the provided documents."

Context:
{context}

Question: {request.question}

Answer (with inline citations):"""
 # 4. Call Claude
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.content[0].text

        logger.info(
            f"/rag-chat succeeded - input_tokens={response.usage.input_tokens}, "
            f"output_tokens={response.usage.output_tokens}"
        )
        # 5. Build the structured response
        return RAGResponse(
            question=request.question,
            answer=answer,
            retrieved_chunks=[
                RetrievedChunk(
                    text=chunk,
                    source=meta["source"],
                    chunk_index=meta["chunk_index"],
                )
                for chunk, meta in zip(retrieved_chunks, retrieved_metadata)
            ],
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    except anthropic.AuthenticationError:
        raise HTTPException(status_code=500, detail="Server configuration error: invalid API key")

    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="Service is busy. Please try again in a moment.")

    except anthropic.APIConnectionError:
        raise HTTPException(status_code=503, detail="Could not reach AI service. Please try again.")

    except Exception as e:
        logger.exception("Unexpected error in /rag-chat")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again.")