# FinancialQA-Assistant

A local, privacy-preserving question-answering system for financial documents using FastAPI, sentence-transformers, and Ollama Mistral. The system extracts content from raw PDFs, performs semantic search over chunked embeddings, and returns precise answers with a clean HTML UI.

---

## Features

- **FastAPI-based backend** for real-time inference
- **PDF ingestion** using `pdfplumber`
- **Semantic search** using `sentence-transformers`
- **LLM integration** using **Ollama Mistral** for local answer generation
- **Simple UI** using HTML/CSS/JS (chat-style interface)
- Fully **offline** and **privacy-respecting**

---

## Interface Preview

### Main Chat Interface

![Chat UI](Images/interface_ui.png)

### Example Query 1

![Example 1](Images/example1.png)

### Example Query 2

![Example 2](Images/example2.png)

---

## Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/Amaan-developpeur/FinancialQA-Assistant.git
cd FinancialQA-Assistant

```
## Create a virtual environment (optional but recommended)
```
python -m venv .venv
.\.venv\Scripts\activate
```
## Install dependencies
```
pip install -r requirements.txt
```
## Start Ollama and pull Mistral (if not done) [Manually Install Ollama from Official Website]
```
ollama run mistral


```
## Run the Application
```
uvicorn app.main1:app --reload

Then open your browser and visit:
http://127.0.0.1:8000
```

## Project Structure
```
financial-qa/
├── app/
│   ├── main.py               # Swagget.UI can be openned
     ├── main1.py             # FastAPI app entrypoint
│   ├── query_engine.py         # Embedding search logic
│   ├── templates/chat.html     # Jinja2-based UI
│   ├── static/                 # CSS & JS files
│   └── utils/
│       ├── local_generate.py   # LLM inference using Ollama
│       └── system_prompt.py    # System prompt builder
├── data/
├── scripts/                      
├── Images/                     # Screenshots for documentation
├── requirements.txt
├── .gitignore
└── README.md


```
## LICENSE
```

---

This project is licensed under the MIT License.
Free to use, modify, and distribute this software for both personal and commercial purposes, provided that proper attribution is given.




