from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from query import answer

app = FastAPI()

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask(request: Question):
    result = answer(request.question)
    return {"answer": result}