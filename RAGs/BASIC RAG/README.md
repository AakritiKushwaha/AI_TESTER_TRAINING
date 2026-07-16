# RAG Explorer

A lightweight Retrieval-Augmented Generation (RAG) web app built with React + Vite (frontend) and FastAPI (backend). It ingests a PDF from the `data/` folder, chunks the text, generates embeddings, stores them in a local ChromaDB instance, retrieves the top 4 most relevant chunks for a user query, and passes them to Groq's LLM for an answer with inline citations — all running locally with no cloud dependencies.

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

Open **http://localhost:3000** (or whichever port Vite assigns) in a browser.

## Usage

The UI is a two-column layout with a horizontal pipeline stepper at the top showing the 6 RAG stages: **PDF → Chunk → Embed → Store → Retrieve → Answer**.

### Ingestion (left column)

1. Click **Ingest folder** to read the first PDF from `data/`, chunk it (800-char sliding window, 120-char overlap), generate embeddings via all-MiniLM-L6-v2, and store everything in the local ChromaDB store (`chroma_data/`).
2. Alternatively, **drag and drop** a `.pdf`, `.txt`, or `.md` file onto the drop zone — or click it to browse — to ingest a custom file.
3. Click **Reset** to delete the ChromaDB collection and start fresh.
4. After ingestion, four stat cards appear: **Pages**, **Chunks**, **Embed dims**, and **Stored** counts.
5. A **sample embedding preview** shows the first 8 dimensions of one embedding vector.
6. An expandable **chunk preview** list shows each chunk's index and character count — click to view the full text.

### Ask & Answer (right column)

1. Click any **suggestion chip** (auto-generated from the document) to populate the textarea, or type your own question.
2. Click **Ask** to retrieve the top 4 most relevant chunks from ChromaDB and send them (with your query) to Groq's Llama 3.3 70B model.
3. The answer displays with inline citation badges (e.g., `【Chunk 1】`) next to each claim, the model name, and token usage.
4. The top 4 retrieved source chunks are shown below the answer for transparency.

The stepper advances through each stage as you go, making the entire RAG pipeline visible.

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/ingest` | POST | Read first PDF from `data/`, chunk, embed, store in ChromaDB |
| `/api/ingest_file` | POST | Upload a `.pdf`, `.txt`, or `.md` file and ingest it |
| `/api/reset` | POST | Delete the ChromaDB collection |
| `/api/suggestions` | POST | Generate 4 suggested questions from the document via Groq |
| `/api/query` | POST | Submit `{query: "..."}`, retrieve top 4 chunks, answer via Groq |

### Quick test with curl

```bash
# Ingest
curl -X POST http://127.0.0.1:8000/api/ingest

# Query
curl -X POST http://127.0.0.1:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What does the login dashboard support?"}'

# Get suggestions
curl -X POST http://127.0.0.1:8000/api/suggestions

# Upload a file
curl -X POST http://127.0.0.1:8000/api/ingest_file \
  -F "file=@my-document.pdf"

# Reset
curl -X POST http://127.0.0.1:8000/api/reset
```

## Project Structure

| Path | Purpose |
|---|---|
| `backend.py` | FastAPI server — ingestion, embedding, ChromaDB queries, Groq API calls |
| `src/App.jsx` | React UI — pipeline stepper, ingestion controls, query input, answer + sources |
| `src/main.jsx` | React entry point |
| `src/index.css` | Dark-themed UI styles |
| `index.html` | Vite HTML shell |
| `vite.config.js` | Vite config — proxies `/api` → `localhost:8000` |
| `data/` | Place your PDF here (auto-discovered) |
| `chroma_data/` | Local on-disk vector store (auto-created on ingest) |
| `prompt/prompt.md` | Original project prompt / requirements |
| `cgi.py` | Compatibility shim for Python 3.14+ (ChromaDB dependency) |
| `.env` | Environment variables (`GROQ_API_KEY=...`) |
| `requirements.txt` | Python dependencies |
| `package.json` | Frontend dependencies |

## Environment

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key
```

## Related Projects

- **Langflow Naive RAG with RAG Explorer UI** (`../LANGFLOW_NAIVE_RAG_WITH_RAG_EXPLORER_UI/`) — Same RAG Explorer interface but with a Langflow-based backend (ChromaDB + Mistral Embeddings + Groq LLM). Deployable to Vercel with an ngrok-exposed Langflow instance.
