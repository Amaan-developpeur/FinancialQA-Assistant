# app/utils/metrics.py
import time

try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
    PROM_OK = True
except Exception:
    PROM_OK = False
    Counter = Histogram = object  # dummy placeholders

# define metrics (if available)
if PROM_OK:
    RAG_REQUESTS = Counter("rag_requests_total", "Total /query requests", ["endpoint", "cache_hit"])
    RAG_LATENCY = Histogram("rag_latency_ms", "Total pipeline latency (ms)", ["endpoint"], buckets=(50,100,200,400,800,1600,3200,6400,12800))
    RETRIEVAL_LATENCY = Histogram("rag_retrieval_ms", "Vector retrieval latency (ms)")
    LLM_LATENCY = Histogram("rag_llm_ms", "LLM generation latency (ms)")

def metrics_response():
    if not PROM_OK:
        return ("prometheus_client not installed", "text/plain")
    return (generate_latest(), CONTENT_TYPE_LATEST)

class LatencyTimer:
    def __enter__(self):
        self.t0 = time.time()
        return self
    def __exit__(self, exc_type, exc, tb):
        self.ms = (time.time() - self.t0) * 1000
