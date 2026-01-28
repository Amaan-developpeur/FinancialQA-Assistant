# Financial QA Assistant – Version 2 (RAG System)
**Retrieval-Augmented Generation System for Financial Document Intelligence**  
_End-to-end RAG platform for financial document understanding and Q&A automation._

> **Previous release:** [Version 1 (Baseline RAG Prototype)](https://github.com/Amaan-developpeur/FinancialQA-Assistant/tree/main)
---

## Live UI Preview
![Financial QA Assistant Screenshot](frontend/ui_screenshot.png)  
> Real-time streamed answers with context citations and latency tracking.

---

## Overview
A local Retrieval-Augmented Generation (RAG) system for asking questions over financial PDFs (annual reports, statements, disclosures). The goal is to demonstrate **practical RAG system design**, not to build a production financial advisor.

---

## What It Does

Users ask questions in natural language.  
The system retrieves relevant parts of financial documents and then uses a local LLM to generate an answer grounded in that text.
---

### System Flow
```
PDFs → Chunking → Embeddings → Chroma Vector Store → FastAPI → Ollama → Live Web UI
```

Built with:
- **FastAPI** backend  
- **ChromaDB** persistent vector store  
- **SentenceTransformer (MiniLM-L6-v2)** embeddings  
- **Ollama + Gemma/Mistral** local LLMs  
- **HTML + JS** streaming frontend  

---

## V1 vs V2
**v1**
- Modular code, structured extraction and embedding
- Pandas + numpy-based retrieval
- No persistent vector database

**v2**
- Persistent Chroma vector store
- Parallel PDF extraction
- Precomputed embeddings

---

## System Architecture
```
Frontend (HTML + JS)
        │  fetch / stream
        ▼
FastAPI Backend ──► Extraction → Embedding → Vector Search → LLM Stream
                        (pdfplumber)   (MiniLM)   (ChromaDB)   (Ollama)
                           │
                      Persisted in /data/
```

---

## Quick Start

### Prerequisites
- Python ≥ 3.10 (Anaconda OK)  
- Ollama installed and running (`ollama serve`)  
- Pull a model:
  ```bash
  ollama pull gemma:2b
  ```
  *(You can replace with `mistral:7b`, `phi3:mini`, etc.)*

### Run the Backend
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Run the Frontend
```bash
cd frontend
python -m http.server 8080
```
Then open → [http://127.0.0.1:8080](http://127.0.0.1:8080)

---

### Performance Notes

Performance is tied to local setup and LLM inference, not just retrieval. Typical behavior on CPU:

- Vector search: sub-second
- Prompt construction: negligible
- Local LLM response: tens of seconds

Improvements in v2 target: **scalability and modular design**

---

## Core Modules

| Module | Description |
| ------- | ------------ |
| `extract/extract_texts.py` | Parallel text chunker (pdfplumber + overlap windowing) |
| `store/chroma_ingest.py` | Vector embedding ingest to persistent Chroma |
| `store/vector_search.py` | Semantic similarity retrieval (top-k) |
| `llm/prompt_builder.py` | Context + metadata prompt formatter |
| `llm/ollama_stream.py` | Token-level streaming generator |
| `main.py` | FastAPI entrypoint (`/query`, `/query/stream`, `/health`) |

---







