# app/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from app.query_engine import get_top_k_similar_chunks
from app.utils.system_prompt import system_prompt
from app.utils.local_generate import local_generate

app = FastAPI(title="Financial QA Assistant")

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

@app.post("/ask")
def ask_question(query: QueryRequest):
    chunks = get_top_k_similar_chunks(query.question, k=query.top_k)
    prompt = system_prompt(chunks, query.question)
    response = local_generate(prompt)
    return {"Generated Answer": response, "prompt_used": prompt}
