# app/store/vector_search.py
import time
from pathlib import Path
import numpy as np
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

from app.utils.cache import SmartCache   # new import for caching

# ===== Paths & Config =====
BASE_DIR = Path(__file__).resolve().parents[2]
VECTOR_DIR = BASE_DIR / "data" / "vector_store"
COLLECTION_NAME = "financial_chunks"

# ===== Initialize Clients =====
client = PersistentClient(path=str(VECTOR_DIR))
collection = client.get_collection(COLLECTION_NAME)
model = SentenceTransformer("all-MiniLM-L6-v2")
cache = SmartCache()  # tries Redis; falls back to in-memory TTL cache


# ===== Main Retrieval Function =====
def get_top_k_chunks(question: str, k: int = 5):
    """
    Embed the question, search Chroma, and return top-k chunks with metadata.
    Uses SmartCache to avoid redundant retrievals.
    """
    # --- Cache lookup ---
    key = cache.make_query_key(question, k)
    cached = cache.get_json(key)
    if cached:
        cached["cache_hit"] = True
        return cached

    # --- Compute embedding + Chroma query ---
    start = time.time()
    q_emb = model.encode([question])
    res = collection.query(
        query_embeddings=np.array(q_emb),
        n_results=k,
        include=["metadatas", "documents", "distances"],
    )
    latency = round((time.time() - start) * 1000, 2)

    # --- Format results ---
    results = []
    for meta, text, dist in zip(
        res["metadatas"][0], res["documents"][0], res["distances"][0]
    ):
        results.append(
            {
                "filename": meta["filename"],
                "page": meta["page"],
                "distance": round(dist, 3),
                "text": (text[:400] + "...") if text else "",
            }
        )

    # --- Persist to cache ---
    payload = {"results": results, "latency_ms": latency, "cache_hit": False}
    cache.set_json(key, payload)

    return payload
