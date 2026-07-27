AI Engineer Journey
## 🚀 Live Demos

### Flagship — IT Helpdesk RAG (Days 27–34)

A grounded question-answering API over real (anonymized) IT documentation.
Hybrid retrieval, an automated eval suite, and a 9/9 measured score.

**API docs (Swagger UI):** https://flagship-helpdesk-rag.onrender.com/docs

Try it: expand `POST /ask` → **Try it out** → send:

```json
{"question": "How often does my password expire?"}
```

> **Note:** Free-tier Render instance — the first request after ~15 min idle
> takes ~50 seconds (cold start). After that, responses are fast.

---

### Agent backend (Days 15–21)

A multi-tool agent (calculator, directory, weather, RAG) with session memory.

**API docs (Swagger UI):** https://ai-engineer-journey-0agd.onrender.com/docs

Try it: expand `POST /agent-chat` → **Try it out** → send:

```json
{"message": "What is 25 times 47?", "session_id": "demo-1"}
```

> **Note:** Same free-tier cold start applies (~50s on first request).

---

My 3-month journey from backend developer (C#/.NET) to AI Engineer (Python).

Start date: May 1, 2026 Target: August 1, 2026 Goal: Land a full-time AI Engineer role
Plan

    Month 1 (May): Python fundamentals, FastAPI, LLM APIs, RAG systems, agents
    Month 2 (June): Flagship agentic project, frontend, deployment
    Month 3 (July): Resume, interview prep, job applications

Progress
Phase 1 — Foundations (Days 1–4)

    ✅ Day 1 (May 1): Python basics — variables, lists, dicts, functions, list comprehensions
    ✅ Day 2 (May 3): OOP — classes, __init__, __str__, error handling, file I/O, mini project (employee manager)
    ✅ Day 3 (May 4): FastAPI CRUD API — REST endpoints, Pydantic models, auto-validation, Swagger docs, persistence
    ✅ Day 4 (May 6): First Claude API integration — Anthropic SDK, .env secrets, AI-powered FastAPI endpoint

Phase 2 — AI Backend (Days 5–6)

    ✅ Day 5 (May 7): Streaming responses + multi-turn conversation memory — chatbot backend
    ✅ Day 6 (May 8): Production resilience — structured error handling, retry logic with exponential backoff (tenacity), structured logging

Phase 3 — RAG System (Days 7–8)

    ✅ Day 7 (May 9): First RAG — ChromaDB vector store, all-MiniLM-L6-v2 embeddings, semantic search, grounded generation
    ✅ Day 8: Better RAG — RecursiveCharacterTextSplitter, chunk metadata, inline [Source: Chunk N] citations, LangChain

Phase 4 — RAG as a Service (Days 9–11)

    ✅ Day 9: RAG as a FastAPI endpoint — POST /rag-chat, module-level client init, structured JSON response
    ✅ Day 10: RAG evaluation — 7-question eval dataset, automated grader, baseline 86% score
    ✅ Day 11: Hybrid search — BM25 + vector + Reciprocal Rank Fusion (RRF). Eval climbed 86% → 100%

Phase 5 — Multi-Document RAG (Days 12–14)

    ✅ Day 12: Multi-document support — loaded .txt + .pdf (235K-char Wikipedia article). Discovered the noise effect: 100% → 71% on the same eval at 684 chunks
    ✅ Day 13: Metadata filtering — source_filter propagated through vector + keyword + hybrid search. Eval recovered 71% → 100% on the noisy multi-doc database
    ✅ Day 14: Reranking — cross-encoder (ms-marco-MiniLM-L-6-v2) as a second-stage filter on top of hybrid retrieval. Eval climbed 71% → 86% without source filter. Identified the recall ceiling

Phase 6 — Agents and Tool Use (Days 15–18)

    ✅ Day 15: First agent — minimal calculator-tool agent. Verified the agent loop: tool_use vs end_turn. Empirically proved "knowing when NOT to act"
    ✅ Day 16: Multi-tool agent — added get_weather + search_company_directory. 5-test routing matrix, including a query that triggered parallel tool use (two tool_use blocks in a single Claude response)
    ✅ Day 17: Agentic RAG — wrapped the entire two-stage retrieval pipeline (hybrid search + reranker) as a single agent tool. Claude now decides per-query whether retrieval is even needed. Description phrasing ("use this whenever...") routes overlapping-knowledge questions through the tool — the lever between grounding and latency
    ✅ Day 18: Sequential tool chaining — same run_agent() loop, different question structure. "Weather where David works?" → Claude called directory first, then weather, because the second tool's input was defined by the first's output. Latency scales with dependency depth, not tool count. API calls = sequential steps + 1, not tool calls + 1

Phase 7 — Stateful Agents & Production Shape (Days 19–21)

    ✅ Day 19: Stateful agent memory — module-level session_id-indexed dict persists message history across run_agent() calls. Two-turn proof: turn 1 fetched David's location via the directory tool; turn 2 asked "what's the weather there?" — Claude resolved "there" to Toronto from the replayed turn-1 tool blocks. Same statelessness pattern as Day 5, applied across function calls instead of across API calls.
    ✅ Day 20: Agent over HTTP — exposed run_agent() as POST /agent-chat. session_id field threads multi-turn conversations through stateless HTTP requests. Hardened with try/except mapping RateLimitError → 429, APIConnectionError → 503, AuthenticationError / BadRequestError / Exception → 500. The production chat pattern: session store outside, agent loop inside, tools Claude routes to.
    ✅ Day 21: Unit tests for the agent endpoint — pytest + FastAPI TestClient + unittest.mock.patch. Verified all 4 error branches (429 / 503 / 500) by replacing run_agent with controllable fakes that raise specific Anthropic exceptions. Five tests, sub-second per test, zero API credits, zero flakiness. The mental model: you're not testing Anthropic — you're testing your code's reaction to Anthropic's failures.

    ---

# PHASE 6 — Flagship Project (Days 27–28)
**Folder:** `flagship/`

## Day 27 — Rebuilt indexing pipeline (clean, multi-doc)
- Rebuilt `loader.py` + `index_docs.py` for the flagship IT-helpdesk RAG. Folder-loop loader (`iterdir`, `is_file()` guard) — data decoupled from logic. Source-prefixed IDs so `chunk_0` from two files don't collide. Metadata: `source`, `chunk_index`, `total_chunks`.
- Real cleaned IT docs: `vpn-expiration.txt` + `change-password.txt` (company name + domain removed before indexing).
- **Status:** ✅ Complete.

## Day 28 — Finished the RAG query side + demoed to manager
- **Built `query.py`** — the query half. Four blocks: (1) connect + `count()` sanity check, (2) `collection.query()` retrieves 3 closest chunks with metadata, (3) glue chunks into context + grounded prompt, (4) send to Claude Haiku, print grounded answer.
- **The handshake:** query and index share NO memory — the disk is the only channel. Must match `path="./chroma_db"` + collection `name="maple_ai_docs"` exactly, or Chroma returns empty with NO error. Used `get_collection` (read), not `create_collection` (write).
- **Grounding:** the word ONLY in the prompt + "say I don't know" fallback = answers from OUR docs, not training. Debugged one layer at a time (printed raw chunks before wiring Claude).
- **Tested:** "When does my VPN expire?" → correct grounded answer from `vpn-expiration.txt`.
- **Security:** `.env` + `.gitignore` set up in flagship. `git status` before staging; named files in `git add`, never `git add .`.
- **Real-world win:** Demoed to my manager — he liked it.
- **Status:** ✅ Complete, committed + pushed (6e2eb48).

### Day 29 — Flagship Eval Dataset
- Built `eval_dataset.py` — 7 test cases for the IT-helpdesk RAG (same pattern as Day 10).
- 4 answerable cases (expected_facts pulled from the real docs) + 3 refusal cases (expected_refusal: True) for topics the docs don't cover.
- Purpose: a regression tripwire — establishes the "before" so Day 30's hybrid upgrade can be measured, not guessed. "Can't improve what I can't measure."

### Day 30 — Eval Grader + answer() Refactor
- Refactored `query.py` into a reusable `answer(question)` function — CLI and grader share one code path.
- Built `eval.py` — automated grader, 3 branches (should-refuse, over-refusal, fact-check), prints a score.
- Baseline: 7/7. Caught a false negative live ("3 months" vs "three months") — fixed the test, not the working code.

Stack

    Language: Python 3.x
    Web framework: FastAPI + Uvicorn
    Data validation: Pydantic
    LLM API: Anthropic Claude (Sonnet 4.6 for agents, Haiku 4.5 for RAG summarization)
    Vector DB: ChromaDB (PersistentClient)
    Embeddings: all-MiniLM-L6-v2 (local, free)
    Chunking: langchain-text-splitters (RecursiveCharacterTextSplitter)
    Keyword search: rank-bm25
    Reranking: sentence-transformers (cross-encoder)
    Agents / Tool use: Anthropic SDK tools parameter, custom agent loop
    Agentic RAG: RAG pipeline wrapped as a single agent tool
   Resilience: tenacity (retries with exponential backoff)
    Session store: module-level dict, session_id → message history (Redis-upgradable)
    Testing: pytest, FastAPI TestClient, unittest.mock.patch
    Env management: python-dotenv, .venv

Repository Structure

ai-engineer-journey/
├── week1-python-basics/      # Days 1–2: Python fundamentals + OOP
├── week2-fastapi/            # Days 3–6: FastAPI + Claude integration + resilience
└── week3-rag/                # Days 7–18: RAG pipeline + agents
    ├── index_docs.py         # Indexing (Day 7)
    ├── query.py              # Querying (Day 7)
    ├── main.py               # RAG FastAPI endpoint (Day 9)
    ├── eval_dataset.py       # Eval questions (Day 10)
    ├── eval.py               # Automated grader (Days 10, 11, 13, 14)
    ├── retrieval.py          # Hybrid search + reranking (Days 11, 14)
    ├── loader.py             # Multi-doc loader, .txt + .pdf (Day 12)
    ├── agent_demo.py         # Multi-tool agent + chaining + session state (Days 15–16, 18, 19)
    ├── agentic_rag.py        # Agent + RAG composition (Day 17)
    ├── agent_main.py         # Agent over HTTP, POST /agent-chat (Day 20)
    ├── tests/
    │   └── test_agent_main.py  # pytest + mock-based endpoint tests (Day 21)
    └── docs/                 # Source documents
    └── flagship/                # Days 27–28: IT-helpdesk RAG (query.py, index_docs.py, loader.py, docs/)

Highlights

    The grounding moment (Day 7). Asked "what's the stock price?" — RAG returned financially-themed chunks, but Claude refused to fabricate. Proof that grounding works as designed.
    Hybrid search win (Day 11). Same eval, scientific A/B. 86% → 100% by adding BM25 + RRF on top of vector search.
    The noise effect (Day 12). 100% → 71% when scaling to multi-doc with 684 chunks. Diagnosed two specific failure modes: BM25 signal dilution and vector recall pressure.
    Metadata filtering (Day 13). 71% → 100% on the noisy database by scoping searches with a source filter. "Scope before you search."
    Reranking + the recall ceiling (Day 14). Cross-encoder reranking took 71% → 86% on the noisy multi-doc database. The remaining 14% was recall failure in stage one — reranking can only re-score what the retriever surfaces.
    Parallel tool use (Day 16). Built a 3-tool agent. One query ("weather + contact David") triggered TWO tool_use blocks in a single Claude response — independent tools batched, one API round-trip instead of two.
    Agentic RAG composition (Day 17). Wrapped my full two-stage retrieval pipeline as a single agent tool. Claude decides per-query whether retrieval is needed. Observed that tool description phrasing controls both whether the tool fires and what arguments Claude passes to it.
   Sequential chaining and dependency depth (Day 18). Same loop, same tools as Day 16. Different question structure ("weather where David works") → Claude inferred the data dependency and ran the tools sequentially. Latency scales with dependency depth, not tool count.
    Stateful agent memory (Day 19). session_id-indexed dict outside the agent loop persists tool_use and tool_result blocks across turns. Turn 2 asked "what's the weather there?" with no mention of "Toronto" or "David" — Claude resolved both referents from the replayed turn-1 history. Same statelessness/replay pattern as Day 5, at a different timescale.
    Testing rigor (Day 21). Wrote pytest + TestClient + mock.patch tests for every error branch in the /agent-chat endpoint. The mental model: you're not testing Anthropic — you're testing your code's reaction to Anthropic's failures. Five tests, sub-second per test, zero API credits burned.
    9. **The handshake / silent failure (Day 28)** — Indexing and querying share no memory; the disk is their only channel. The DB path and collection name are the handshake — mismatch them and the vector DB returns empty with *no error*. So I verify with a `count()` check before building the query layer on top. *Knowing the silent failure modes is the senior signal.*
10. **The flagship real-world win (Day 28)** — Identified a repetitive task in my own IT job (VPN/password questions), built a RAG system over our own *cleaned* documents (company name + domain stripped before indexing), and demoed it to my manager, who wanted it for the team. *Build → ship → real adoption interest — not a tutorial.*

Last updated: July 6, 2026 — Day 28 complete (RAG query side finished, demoed to manager)


