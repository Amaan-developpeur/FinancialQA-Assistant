# app/llm/ollama_client.py
import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"

def query_ollama(prompt: str, model: str = "gemma3:4b"):
    """Send prompt to local Ollama LLM and return text output."""
    start = time.time()
    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60
        )
        r.raise_for_status()
        text = r.json().get("response", "").strip()
    except Exception as e:
        text = f"[LLM_ERROR] {e}"
    latency = round((time.time() - start) * 1000, 2)
    return {"answer": text, "latency_ms": latency}
