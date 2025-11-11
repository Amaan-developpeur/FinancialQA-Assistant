# app/llm/ollama_stream.py
import json
import time
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def stream_ollama(prompt: str, model: str = "gemma3:4b", timeout: int = 180):
    """
    Stream tokens from Ollama. Yields plain text chunks.
    Prints [END_STREAM latency_ms=...] cleanly at the end.
    Handles partial or broken connections gracefully.
    """
    started = time.time()
    try:
        with requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": True},
            timeout=(10, 180),
            stream=True,
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if "response" in obj:
                    yield obj["response"]
                if obj.get("done"):
                    break
    except requests.exceptions.ChunkedEncodingError:
        yield "\n[LLM_STREAM_WARNING] Stream ended early (client closed connection)\n"
    except Exception as e:
        yield f"\n[LLM_STREAM_ERROR] {e}\n"
    finally:
        latency = round((time.time() - started) * 1000, 2)
        yield f"\n\n[END_STREAM latency_ms={latency}]"
