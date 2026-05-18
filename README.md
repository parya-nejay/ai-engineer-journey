# AI Engineer Journey

My 3-month journey from backend developer (C#/.NET) to AI Engineer (Python).

**Start date:** May 1, 2026
**Target:** August 1, 2026
**Goal:** Land a full-time AI Engineer role

## Plan

- **Month 1 (May):** Python fundamentals, FastAPI, LLM APIs, RAG systems, agents
- **Month 2 (June):** Flagship agentic project, frontend, deployment
- **Month 3 (July):** Resume, interview prep, job applications

## Progress

### Phase 1 — Foundations (Days 1–4)

- ✅ Day 1 (May 1): Python basics — variables, lists, dicts, functions, list comprehensions
- ✅ Day 2 (May 3): OOP — classes, `__init__`, `__str__`, error handling, file I/O, mini project (employee manager)
- ✅ Day 3 (May 4): FastAPI CRUD API — REST endpoints, Pydantic models, auto-validation, Swagger docs, persistence
- ✅ Day 4 (May 6): First Claude API integration — Anthropic SDK, `.env` secrets, AI-powered FastAPI endpoint

### Phase 2 — AI Backend (Days 5–6)

- ✅ Day 5 (May 7): Streaming responses + multi-turn conversation memory — chatbot backend
- ✅ Day 6 (May 8): Production resilience — structured error handling, retry logic with exponential backoff (`tenacity`), structured logging

### Phase 3 — RAG System (Days 7–8)

- ✅ Day 7 (May 9): First RAG — ChromaDB vector store, `all-MiniLM-L6-v2` embeddings, semantic search, grounded generation
- ✅ Day 8: Better RAG — `RecursiveCharacterTextSplitter`, chunk metadata, inline `[Source: Chunk N]` citations, LangChain

### Phase 4 — RAG as a Service (Days 9–11)

- ✅ Day 9: RAG as a FastAPI endpoint — `POST /rag-chat`, module-level client init, structured JSON response
- ✅ Day 10: RAG evaluation — 7-question eval dataset, automated grader, baseline 86% score
- ✅ Day 11: Hybrid search — BM25 + vector + Reciprocal Rank Fusion (RRF). Eval climbed 86% → **100%**

### Phase 5 — Multi-Document RAG (Days 12–14)

- ✅ Day 12: Multi-document support — loaded `.txt` + `.pdf` (235K-char Wikipedia article). Discovered the **noise effect**: 100% → 71% on the same eval at 684 chunks
- ✅ Day 13: Metadata filtering — `source_filter` propagated through vector + keyword + hybrid search. Eval recovered 71% → **100%** on the noisy multi-doc database
- ✅ Day 14: Reranking — cross-encoder (`ms-marco-MiniLM-L-6-v2`) as a second-stage filter on top of hybrid retrieval. Eval climbed 71% → 86% without source filter. Identified the recall ceiling

### Phase 6 — Agents and Tool Use (Days 15–16)

- ✅ Day 15: First agent — minimal calculator-tool agent. Verified the agent loop: `tool_use` vs `end_turn`. Empirically proved "knowing when NOT to act"
- ✅ Day 16: Multi-tool agent — added `get_weather` + `search_company_directory`. 5-test routing matrix, including a query that triggered **parallel tool use** (two `tool_use` blocks in a single Claude response)

## Stack

- **Language:** Python 3.x
- **Web framework:** FastAPI + Uvicorn
- **Data validation:** Pydantic
- **LLM API:** Anthropic Claude (via official SDK)
- **Vector DB:** ChromaDB (`PersistentClient`)
- **Embeddings:** `all-MiniLM-L6-v2` (local, free)
- **Chunking:** `langchain-text-splitters` (`RecursiveCharacterTextSplitter`)
- **Keyword search:** `rank-bm25`
- **Reranking:** `sentence-transformers` (cross-encoder)
- **Agents / Tool use:** Anthropic SDK `tools` parameter, custom agent loop
- **Resilience:** `tenacity` (retries with exponential backoff)
- **Env management:** `python-dotenv`, `.venv`
- **Frontend:** Next.js (planned)
- **Deployment:** Vercel + Render/Railway (planned)

## Repository Structure

```
ai-engineer-journey/
├── week1-python-basics/      # Days 1–2: Python fundamentals + OOP
├── week2-fastapi/            # Days 3–6: FastAPI + Claude integration + resilience
└── week3-rag/                # Days 7–16: RAG pipeline + agents
    ├── index_docs.py         # Indexing (Day 7)
    ├── query.py              # Querying (Day 7)
    ├── main.py               # RAG FastAPI endpoint (Day 9)
    ├── eval_dataset.py       # Eval questions (Day 10)
    ├── eval.py               # Automated grader (Days 10, 11, 13, 14)
    ├── retrieval.py          # Hybrid search + reranking (Days 11, 14)
    ├── loader.py             # Multi-doc loader, .txt + .pdf (Day 12)
    ├── agent_demo.py         # Multi-tool agent (Days 15–16)
    └── docs/                 # Source documents
```

## Highlights

- **The grounding moment (Day 7).** Asked "what's the stock price?" — RAG returned financially-themed chunks, but Claude refused to fabricate. Proof that grounding works as designed.
- **Hybrid search win (Day 11).** Same eval, scientific A/B. 86% → 100% by adding BM25 + RRF on top of vector search.
- **The noise effect (Day 12).** 100% → 71% when scaling to multi-doc with 684 chunks. Diagnosed two specific failure modes: BM25 signal dilution and vector recall pressure.
- **Metadata filtering (Day 13).** 71% → 100% on the noisy database by scoping searches with a source filter. "Scope before you search."
- **Reranking + the recall ceiling (Day 14).** Cross-encoder reranking took 71% → 86% on the noisy multi-doc database. The remaining 14% was *recall* failure in stage one — reranking can only re-score what the retriever surfaces.
- **Parallel tool use (Day 16).** Built a 3-tool agent. One query ("weather + contact David") triggered TWO `tool_use` blocks in a single Claude response — independent tools batched, one API round-trip instead of two.

---

*Last updated: May 17, 2026 — Day 16*