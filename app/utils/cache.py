# app/utils/cache.py
import json, time, os, threading, hashlib
from typing import Optional

DEFAULT_TTL = int(os.getenv("CACHE_TTL_SECONDS", "86400"))  # 24h

def _now(): return int(time.time())

def _hash_key(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def normalize_question(q: str) -> str:
    return " ".join(q.lower().split())

class InMemoryTTLCache:
    """Tiny TTL cache with size cap & thread safety."""
    def __init__(self, max_items: int = 5000):
        self.max_items = max_items
        self.store = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[str]:
        with self.lock:
            item = self.store.get(key)
            if not item: return None
            value, exp = item
            if exp < _now():
                del self.store[key]; return None
            return value

    def setex(self, key: str, ttl: int, value: str):
        with self.lock:
            if len(self.store) >= self.max_items:
                # drop an arbitrary key (good enough)
                self.store.pop(next(iter(self.store)))
            self.store[key] = (value, _now() + ttl)

class SmartCache:
    """Uses Redis if available; otherwise in-memory TTL cache."""
    def __init__(self, url: str = None):
        self.mem = InMemoryTTLCache()
        self.redis = None
        url = url or os.getenv("REDIS_URL") or "redis://localhost:6379/0"
        try:
            import redis
            self.redis = redis.Redis.from_url(url, socket_timeout=0.5, socket_connect_timeout=0.5)
            # health check
            self.redis.ping()
        except Exception:
            self.redis = None  # fallback to memory

    def get_json(self, key: str):
        try:
            if self.redis:
                v = self.redis.get(key)
            else:
                v = self.mem.get(key)
            return json.loads(v) if v else None
        except Exception:
            return None

    def set_json(self, key: str, obj, ttl: int = DEFAULT_TTL):
        payload = json.dumps(obj, ensure_ascii=False)
        try:
            if self.redis:
                self.redis.setex(key, ttl, payload)
            else:
                self.mem.setex(key, ttl, payload)
        except Exception:
            # best-effort fallback
            self.mem.setex(key, ttl, payload)

    def make_query_key(self, question: str, top_k: int) -> str:
        base = f"q:{normalize_question(question)}|k:{top_k}"
        return f"rag:v1:{_hash_key(base)}"
