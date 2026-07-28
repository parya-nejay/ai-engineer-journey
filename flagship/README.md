# IT Helpdesk RAG

A question-answering API over real IT support documentation. It answers
the questions I actually get asked in my IT job — VPN expiry, password
resets, printer setup, file-upload rules — using our own documents
instead of the model's memory.

Retrieval is vector-only. Hybrid search (BM25 + RRF) is built and tested,
but turned OFF in production because my eval showed it made the answers
worse. See "Engineering decisions" below.

**Measured:** 9/9 on an automated eval · ~7.4s per question in production
(80% of that is retrieval, not the LLM) · ~$0.001 per question.

---

## Live demo

**Swagger UI:** https://flagship-helpdesk-rag.onrender.com/docs

Open `POST /ask` → **Try it out** → send:

```json
{"question": "How often does my password expire?"}
```

Now ask it something the docs don't cover — `{"question": "what is the
wifi password?"}` — and it will say it doesn't know instead of guessing.
That refusal is tested, not hoped for.

> **Free tier:** the first request after ~15 minutes idle takes ~50s
> (cold start). Requests after that are normal speed.

---

## How it works

```
docs/*.txt  ──►  loader.py  ──►  index_docs.py  ──►  chroma_db/
  4 docs         reads folder     chunks + embeds     9 chunks
                                  (500 / 50 overlap)

question  ──►  retrieval.py  ──►  query.py answer()  ──►  Claude Haiku
               vector search      builds grounded          answer
               (top 3 chunks)     prompt                   + sources
                                                           + timings
```

**Two halves that never talk to each other.** Indexing writes to disk.
Querying reads from disk. The only thing connecting them is the ChromaDB
path plus the collection name. Get one character wrong and Chroma returns
zero results with **no error message** — so `answer()` checks the chunk
count before doing anything else.

Grounding is enforced in the prompt: answer *only* from the given
context, otherwise say you don't know.

---

## Measured results

**Quality — automated eval, 9/9**

`eval.py` runs 9 cases against `answer()` and grades them: answerable
questions must contain a specific fact, out-of-scope questions must be
refused.

```
python eval.py
# Score: 9/9
```

A 9/9 only means something because I proved the eval *can* fail — I grew
it from 7 cases to 9 and it immediately caught two false results (a stale
test case, and a grader checking for the wrong keyword).

**Speed — production, measured not guessed**

Every request logs retrieval time and LLM time separately:

| | Local (laptop) | Production (Render free tier) |
|---|---|---|
| Retrieval | ~0.6s | ~6.0s |
| Claude (Haiku) | ~1.0s | ~1.4s |
| **Total** | **~1.6s** | **~7.4s** |

Retrieval is ~80% of production time, and it's **one line** — Chroma
embedding the question. BM25 and RRF cost 0ms. The 10x local-vs-prod gap
is shared CPU on the free tier; I ran an experiment to confirm it wasn't
my code (see below).

**Cost:** ~$0.001 per question (Haiku, ~1.5K in / ~100 out).

---

## Engineering decisions

Three things I built or could have shipped, and turned down instead.

**1. Hybrid search — built it, measured it, switched it off**

Hybrid retrieval (BM25 + vector + Reciprocal Rank Fusion) won big on an
earlier project: 86% → 100%. So I added it here and A/B tested it with the
same eval, using a `mode` flag so both paths run the same code.

```
top_k=3  →  vector 9/9   hybrid 9/9   (eval can't tell them apart)
top_k=1  →  vector 7/9   hybrid 6/9   (hybrid is worse)
```

Hybrid lost. With only one slot, RRF picks the chunk both methods
half-agree on instead of vector's confident pick. And BM25 adds nothing
here: 4 documents, one domain, no rare keywords to match on.

**Decision:** production defaults to `mode="vector"`. The hybrid code and
the flag stay in, ready to re-test when the corpus grows.
*A technique that won on one dataset is not a win on the next.*

**2. A 20x speedup I did not ship**

Retrieval is 80% of latency and it's all query embedding. I benchmarked
two runtimes: ONNX 650ms vs SentenceTransformer 30ms. 20x faster.

I turned it down. SentenceTransformer needs PyTorch — 300-500MB of RAM in
a 512MB container. The container would die. And Claude owns latency the
user actually notices anyway.
*The faster option and the right option are not always the same one.*

**3. The 7s in production is the platform, and I proved it**

Two possible causes: shared-CPU throttling, or the embedding session
being rebuilt on every call. Three warm requests came back flat
(7457 / 7576 / 7434ms) — which separates nothing, because **both causes
predict flat latency.**

So I built a test that could only come out one way: embed two *different*
strings inside one request and log both. A rebuild would make the second
one fast; throttling would leave them equal.

```
call 1:  6087ms / 5598ms      call 3:  6643ms / 5403ms
call 2:  5559ms / 6404ms      call 4:  5624ms / 6091ms
```

No warming curve. Random variance both directions. **Verdict: shared CPU.
Not my code, not fixable on the free tier** — documented as a platform
limit with receipts instead of chased.
*If two explanations predict the same observation, you don't have an
experiment yet.*

---

## Known limits

Honest list. Everything here is a known trade-off, not a surprise.

- **Cold start ~50s.** Render free tier sleeps after 15 min idle. Fixed by
  paying, not by code.
- **~7.4s per request when warm.** Shared CPU (see decision 3). A paid
  instance or a hosted embedding API would fix it.
- **Small corpus: 4 documents, 9 chunks.** Enough to prove the pipeline and
  to make the eval sensitive, not enough to prove behaviour at scale. My
  earlier project showed quality *drops* as documents are added — I expect
  to need metadata filtering here once the corpus grows.
- **No tests yet.** The eval covers answer quality; there are no unit tests
  around the API layer or its error paths. (I wrote those for an earlier
  agent project, so it's a port, not new ground.)
- **No auth or rate limiting** on `/ask`. Fine for a demo, not for real
  users.
- **The index is rebuilt at deploy time**, not stored. `chroma_db/` is a
  build artifact and gitignored, so the Render build command re-runs
  `index_docs.py`.
- **Docs are anonymized.** Company name and domain stripped before
  indexing.

  ---

## Run it locally

```powershell
# from the flagship/ folder
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# confirm you're in THIS project's venv, not another one
python -c "import sys; print(sys.prefix)"

pip install -r requirements.txt
```

Create a `.env` file in `flagship/`:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Build the index, then serve:

```powershell
python index_docs.py          # writes chroma_db/ — 9 chunks
uvicorn main:app --reload     # http://127.0.0.1:8000/docs
python eval.py                # optional: should print 9/9
```

> The `(.venv)` label in your prompt looks identical for every project — it
> does not tell you *which* venv is active. That's why the `sys.prefix`
> check is in the list. I lost time to a project silently running on another
> project's dependencies, twice.

---

## Files

```
flagship/
├── docs/              4 anonymized IT support documents
├── loader.py          reads the docs folder
├── index_docs.py      chunks, embeds, writes chroma_db/
├── retrieval.py       vector search + hybrid (BM25 + RRF, off by default)
├── query.py           answer() — retrieve, ground, call Claude, log
├── main.py            FastAPI: POST /ask
├── eval_dataset.py    9 test cases
├── eval.py            automated grader
└── requirements.txt   10 lines, hand-written from actual imports
```