# main1.py

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.utils.local_generate import local_generate
from app.query_engine import get_top_k_similar_chunks
from app.utils.system_prompt import system_prompt

app = FastAPI(title="Financial QA Chat")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class Query(BaseModel):
    query: str
    top_k: int = 5

@app.get("/", response_class=HTMLResponse)
def serve_ui(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/generate")
def generate(query: Query):
    chunks = get_top_k_similar_chunks(query.query, k=query.top_k)
    prompt = system_prompt(chunks, query.query)
    result = local_generate(prompt)
    return {"response": result}
