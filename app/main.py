# app/main.py
import asyncio
import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
from app.store.vector_search import get_top_k_chunks
from app.llm.prompt_builder import build_prompt
from app.llm.ollama_client import query_ollama
from app.utils.timing import timer
from fastapi.responses import StreamingResponse, PlainTextResponse
from app.llm.prompt_builder import build_prompt
from app.llm.ollama_client import query_ollama  # from earlier M5
from app.llm.ollama_stream import stream_ollama
from app.store.vector_search import get_top_k_chunks
from app.utils.timing import timer
from app.utils.metrics import metrics_response, PROM_OK, RAG_REQUESTS, RAG_LATENCY, RETRIEVAL_LATENCY, LLM_LATENCY, LatencyTimer
import time
from fastapi.middleware.cors import CORSMiddleware


log = logging.getLogger("financial_qa")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
log.addHandler(handler)
log.setLevel(logging.INFO)

app = FastAPI(title="Financial QA Assistant")

# --- CORS setup ---
origins = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# small threadpool for sync tasks
executor = ThreadPoolExecutor(max_workers=4)

class UploadPayload(BaseModel):
    filename: str
    # future: accept file bytes or path

class QueryPayload(BaseModel):
    question: str
    top_k: int = 5

@app.get("/health")
async def health():
    return {"status": "ok", "components": {"chroma": "unknown", "ollama": "unknown"}}

@app.get("/metrics")
async def metrics():
    body, ctype = metrics_response()
    return PlainTextResponse(content=body, media_type=ctype)


@app.post("/upload")
async def upload(payload: UploadPayload, background_tasks: BackgroundTasks):
    # enqueue ingestion in background (placeholder)
    def ingest_task(filename):
        log.info(f"Started ingest: {filename}")
        # TODO: call extractor/inserter
        log.info(f"Finished ingest: {filename}")

    background_tasks.add_task(ingest_task, payload.filename)
    return {"status": "enqueued", "filename": payload.filename}

@app.post("/query")
async def query(payload: QueryPayload):
    question = payload.question.strip()
    if not question:
        raise HTTPException(400, "Empty question")

    loop = asyncio.get_event_loop()

    def sync_pipeline():
        # total latency tracker
        with LatencyTimer() as t_total:
            # --- Retrieval phase ---
            with timer() as t_retr:
                retrieved = get_top_k_chunks(question, payload.top_k)
            retr_ms = retrieved["latency_ms"]

            # --- LLM phase ---
            prompt = build_prompt(retrieved["results"], question)
            llm_output = query_ollama(prompt)

            total_ms = t_total.ms

            # --- Construct response ---
            out = {
                "question": question,
                "context_used": retrieved["results"],
                "cache_hit": retrieved.get("cache_hit", False),
                "vector_latency_ms": retr_ms,
                "llm_latency_ms": llm_output["latency_ms"],
                "total_pipeline_ms": round(total_ms, 2),
                "answer": llm_output["answer"]
            }

            # --- Metrics collection ---
            if PROM_OK:
                RAG_REQUESTS.labels(
                    endpoint="/query",
                    cache_hit=str(out["cache_hit"]).lower()
                ).inc()
                RETRIEVAL_LATENCY.observe(retr_ms)
                LLM_LATENCY.observe(llm_output["latency_ms"])
                RAG_LATENCY.labels(endpoint="/query").observe(total_ms)

            return out

    result = await loop.run_in_executor(executor, sync_pipeline)

    log.info(
        f"/query q='{question[:60]}' "
        f"cache_hit={result.get('cache_hit')} "
        f"retrieval_ms={result.get('vector_latency_ms')} "
        f"llm_ms={result.get('llm_latency_ms')} "
        f"total_ms={result.get('total_pipeline_ms')}"
    )

    return result


@app.post("/query/stream")
async def query_stream(payload: QueryPayload):
    """
    Streams tokens as plain text. Final line includes [END_STREAM latency_ms=...].
    Designed to flush properly on Windows (prevents curl:18).
    """
    question = payload.question.strip()
    if not question:
        raise HTTPException(400, "Empty question")

    loop = asyncio.get_event_loop()

    # --- retrieval (run in threadpool to avoid blocking event loop) ---
    def do_retrieval():
        with timer() as t_retr:
            retrieved = get_top_k_chunks(question, payload.top_k)
        return retrieved

    retrieved = await loop.run_in_executor(executor, do_retrieval)
    prompt = build_prompt(retrieved["results"], question)

    # --- record metrics for retrieval ---
    if PROM_OK:
        RAG_REQUESTS.labels(endpoint="/query/stream", cache_hit=str(retrieved.get("cache_hit", False)).lower()).inc()
        RETRIEVAL_LATENCY.observe(retrieved["latency_ms"])

    # --- define synchronous generator ---
    def sync_gen():
        # show which chunks were used
        yield f"[sources] " + "; ".join(
            f"{c['filename']}#p{c['page']}" for c in retrieved["results"]
        ) + "\n\n"
        started = time.time()
        for chunk in stream_ollama(prompt):  # model stream
            yield chunk
        total_ms = round((time.time() - started) * 1000, 2)
        if PROM_OK:
            RAG_LATENCY.labels(endpoint="/query/stream").observe(total_ms)

    # --- wrap sync generator into async for StreamingResponse ---
    async def async_from_sync(sync_iter):
        for chunk in sync_iter:
            yield chunk
            await asyncio.sleep(0.01)  # allows socket flush (critical on Windows)
        await asyncio.sleep(0.05)  # final flush delay

    return StreamingResponse(
        async_from_sync(sync_gen()),
        media_type="text/plain"
    )
