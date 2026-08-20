from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from query import answer
from retrieval import hybrid_search

hybrid_search("warmup", top_k=1)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://flagship-helpdesk-rag.vercel.app",
        "http://localhost:3000",],
    allow_methods=["POST","GET"],
    allow_credentials=False,
)

@app.get("/health")
def health():
    return {"status": "ok"}

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask(request: Question):
    result = answer(request.question)
    return {"answer": result}