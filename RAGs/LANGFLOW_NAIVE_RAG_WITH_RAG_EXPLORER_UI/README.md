# Langflow Naive RAG with RAG Explorer UI

A transparent RAG (Retrieval-Augmented Generation) Explorer that visualises the entire pipeline — from CSV ingestion through embedding, storage, retrieval, and LLM generation. Unlike a traditional RAG app that does everything inline, this project acts as a **thin proxy** to a **Langflow** flow, so all RAG logic (chunking, embedding, vector search, LLM calls) runs inside Langflow.

**Live demo:** [https://langflow-naive-rag.vercel.app](https://langflow-naive-rag.vercel.app)

## Architecture

```
React + Vite (frontend :5173)
   │  HTTP (fetch)
   ▼
FastAPI (backend :8000) — thin proxy, no RAG logic
   │  POST /api/v1/run/{flow_id}
   ▼
Langflow (service :7860)
   ├── CSV → Split Text → Mistral Embeddings → Chroma DB
   └── User Question → Chroma DB → Groq LLM → Answer
```

The backend **never** touches ChromaDB, embeddings, or Groq directly — all of that lives inside the Langflow flow. The backend simply forwards user questions to Langflow's REST API and parses the response.

## Data Source

- **1,000 real e-commerce test cases** across 10 modules (Login, Registration, Product Search, Product Details, Add to Cart, Wishlist, Checkout, Payment, Order Management, User Profile)
- Stored in `data/ecom_test_cases.csv`
- Ingested into ChromaDB inside Langflow (not by this app)

## Tech Stack

| Component | Tool |
|---|---|
| Frontend | React 18 + Vite 6 |
| Backend | FastAPI + httpx (proxy only) |
| Orchestration | Langflow (REST API) |
| Embeddings | Mistral `mistral-embed` (1024 dims) |
| Vector Store | ChromaDB (persistent, on-disk) |
| LLM Provider | Groq (`llama-3.1-8b-instant`) |
| Deployment | Vercel (monorepo) |

## Prerequisites

- Python 3.10+
- Node.js 18+
- A running [Langflow](https://www.langflow.org/) instance (local or cloud)
- Groq API key (set as a global variable in Langflow)
- Mistral API key (set as a global variable in Langflow)

## Setup

### 1. Environment

Copy the `.env` template and update with your Langflow details:

```
LANGFLOW_URL=http://localhost:7860
LANGFLOW_FLOW_ID=your-flow-uuid
LANGFLOW_API_KEY=your-langflow-api-key
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in a browser.

## Langflow Flow Setup

This project expects a Langlow flow named **NAIVE_RAG** (UUID `a5eeb5af...`) with the following components:

**Ingestion pipeline:**
1. Read File (reads `ecom_test_cases.csv`)
2. Split Text (chunks the CSV rows)
3. MistralAI Embeddings (`mistral-embed`, uses `MISTRAL_API_KEY` global variable)
4. Chroma DB (persistent client, collection `ecom_test_cases`, `persist_directory: ./chroma_data`)

**Retrieval pipeline (wired to Chat Input):**
1. Chroma DB (vector search, uses the same collection)
2. Prompt Template (injects retrieved context + user question)
3. Groq model (`llama-3.1-8b-instant`, uses `GROQ_API_KEY` global variable)
4. Chat Output (final answer)

Set `GROQ_API_KEY` and `MISTRAL_API_KEY` as **Global Variables** in Langflow's **Settings** page.

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/ask` | POST | Send `{question}` → Langflow → answer, model, tokens |
| `/api/pipeline-status` | GET | Langflow connectivity + Chroma collection metadata |
| `/api/test-connection` | GET | Quick Langflow reachability check |

### Example

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Show me login test cases"}'
```

## Project Structure

```
├── backend/
│   ├── main.py              FastAPI proxy (all server logic)
│   └── requirements.txt     Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx          Layout (stepper, left/right panels)
│   │   ├── App.css          Dark theme with orange accents
│   │   └── components/
│   │       ├── PipelineStepper.jsx   6-stage visual stepper
│   │       ├── StatusPanel.jsx       Live Langflow/Chroma status
│   │       └── AskPanel.jsx          Q&A with citations
│   ├── index.html
│   ├── vite.config.js       Dev proxy → localhost:8000
│   └── package.json
├── data/
│   └── ecom_test_cases.csv  1,000 e-commerce test cases
├── prompt/
│   └── prompt.md            Original project specification
├── .env                     Langflow connection details
└── vercel.json              Vercel monorepo deployment config
```

## Deployment (Vercel)

This project is deployed as a Vercel monorepo with two services:

1. **Frontend** — Vite build, served as static assets
2. **Backend** — FastAPI serverless function, rewrites `/api/*` → backend

**Environment variables (set in Vercel dashboard):**
- `LANGFLOW_URL` — publicly accessible Langflow URL (e.g., ngrok tunnel or cloud host)
- `LANGFLOW_FLOW_ID` — your flow UUID
- `LANGFLOW_API_KEY` — your Langflow API key

The backend uses the `ngrok-skip-browser-warning: true` header for ngrok tunnels — you don't need to add this yourself.

```bash
vercel --prod
```

> Note: Hobby tier serverless functions have a 10s timeout. Langlow flow execution may require a Pro plan or faster LLM model.
