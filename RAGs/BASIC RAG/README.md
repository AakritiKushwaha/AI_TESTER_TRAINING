# RAG Explorer

A lightweight Retriever-Augmented Generation (RAG) web application built with React + Vite (frontend) and FastAPI (backend). It ingests a PDF PRD, chunks the text, generates embeddings, stores them in a local ChromaDB instance, retrieves the top 4 most relevant chunks for a user query, and passes them to Groq's LLM for a final answer — all running locally with no cloud dependencies.

## Tech Stack

| Component | Tool |
|---|---|
| Frontend | React + Vite |
| Embedding Model | all-MiniLM-L6-v2 (Sentence Transformers) |
| Vector Store | ChromaDB (embedded / persistent client, on-disk only) |
| LLM Provider | Groq API |
| LLM Model | llama-3.3-70b-versatile |

## Prerequisites

- Python 3.10+
- Node.js 18+

## Setup

### Python backend

```bash
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS / Linux
pip install -r requirements.txt
```

The first time you run the backend, it will download the `all-MiniLM-L6-v2` model (~80 MB) automatically.

### Frontend

```bash
npm install --include=dev
```

> If `NODE_ENV=production` is set globally, npm skips devDependencies. Use `--include=dev` to ensure Vite is installed.

## Running

**Terminal 1 — Backend:**

```bash
venv\Scripts\activate
uvicorn backend:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
npm run dev
```

Open **http://localhost:3000** in a browser.

## Usage

1. Click **Build Local Index** — the app reads the PDF from `data/`, chunks it (800-char sliding window, 120-char overlap), generates embeddings via all-MiniLM-L6-v2, and stores everything in the local ChromaDB store (`chroma_data/`).
2. Type a question about the PRD into the text area.
3. Click **Run Retrieval** — the app retrieves the top 4 most relevant chunks from ChromaDB, sends them (with your query) to Groq's Llama 3.3 70B model, and displays the answer alongside the retrieved source chunks.

The UI makes every RAG pipeline step transparent — source file, chunk count, embedding count, collection name, retrieved chunks, and the final LLM answer are all visible.

## Project Structure

| Path | Purpose |
|---|---|
| `backend.py` | FastAPI server — ingestion, embedding, ChromaDB queries, Groq API calls |
| `src/App.jsx` | React UI — pipeline stats, query input, answer + sources display |
| `src/main.jsx` | React entry point |
| `src/index.css` | UI styles |
| `data/` | Place your PDF here (auto-discovered) |
| `chroma_data/` | Local on-disk vector store (auto-created on ingest) |
| `cgi.py` | Compatibility shim for Python 3.14+ (ChromaDB dependency) |
| `.env` | Environment variables (`GROQ_API_KEY=...`) |
| `requirements.txt` | Python dependencies |
| `package.json` | Frontend dependencies |

## Environment

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key
```
