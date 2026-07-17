# Advanced RAG Explorer

An **end-to-end Advanced Retrieval-Augmented Generation (RAG)** application for querying and generating VWO (Visual Website Optimizer) test cases. Built as a teaching demo for **The Testing Academy**, this project demonstrates production-grade RAG techniques on a real corpus of 5,000 test cases.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Pipeline: Ingestion](#pipeline-ingestion)
- [Pipeline: Chat / Retrieval](#pipeline-chat--retrieval)
- [Project Structure](#project-structure)
- [Components Deep Dive](#components-deep-dive)
  - [Hybrid Embedder (bge-m3)](#1-hybrid-embedder-bge-m3)
  - [Vector Database (Qdrant)](#2-vector-database-qdrant)
  - [Cross-Encoder Reranker (bge-reranker-v2-m3)](#3-cross-encoder-reranker-bge-reranker-v2-m3)
  - [Query Rewriter (GPT-4o-mini)](#4-query-rewriter-gpt-4o-mini)
  - [Answer Generator (DeepSeek Chat)](#5-answer-generator-deepseek-chat)
- [API Endpoints](#api-endpoints)
- [Frontend UI](#frontend-ui)
- [Configuration & Tunables](#configuration--tunables)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [Generating Test Data](#generating-test-data)
- [Troubleshooting](#troubleshooting)
- [Tech Stack Summary](#tech-stack-summary)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INGESTION PIPELINE                              │
│                                                                         │
│  CSV/XLSX ──► pandas DataFrame ──► assemble docs ──► chunk             │
│                                                 │                      │
│                                                 ▼                      │
│                                     bge-m3 (dense + sparse vectors)    │
│                                                 │                      │
│                                                 ▼                      │
│                                    Qdrant (collection: vwo_test_cases) │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         CHAT PIPELINE (per query)                       │
│                                                                         │
│  User Question                                                          │
│       │                                                                 │
│       ▼                                                                 │
│  ❶ Query Rewriting (GPT-4o-mini via Openrouter)                        │
│     └─► 3 alternative phrasings                                        │
│       │                                                                 │
│       ▼                                                                 │
│  ❷ Hybrid Embedding (bge-m3)                                           │
│     └─► dense[1024] + sparse[{token_id: weight}]                       │
│       │                                                                 │
│       ▼                                                                 │
│  ❸ Hybrid Search (Qdrant)                                              │
│     ├─ Dense search (top 20)                                           │
│     └─ Sparse search (top 20)                                          │
│       │                                                                 │
│       ▼                                                                 │
│     RRF Fusion (k=60) ──► merged results                               │
│       │                                                                 │
│       ▼                                                                 │
│  ❹ Cross-Encoder Rerank (bge-reranker-v2-m3)                          │
│     └─► top 4 most relevant chunks                                     │
│       │                                                                 │
│       ▼                                                                 │
│  ❺ Generation (DeepSeek Chat via Openrouter)                           │
│     ├─ Answer mode: grounded Q&A with [Chunk N] citations              │
│     └─ Generate mode: structured test case output                      │
│       │                                                                 │
│       ▼                                                                 │
│     Response with answer + full pipeline trace                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Pipeline: Ingestion

The ingestion pipeline converts raw CSV/XLSX test case files into a searchable vector index.

### Stages

| # | Stage | Description |
|---|-------|-------------|
| 1 | **Read** | Load CSV/XLSX into a pandas DataFrame |
| 2 | **Build Docs** | Combine text columns into document strings, extract metadata (module, priority, JIRA ID, tags) |
| 3 | **Chunk** | Split long documents at sentence boundaries with 150-char overlap between adjacent chunks (default: 1000 chars max) |
| 4 | **Embed** | Generate dense (1024-dim) + sparse (token → weight) vectors using bge-m3 |
| 5 | **Index** | Upsert chunk vectors + payload into Qdrant collection in batches |

### Chunking Algorithm

```
Text ≤ 1000 chars  ──► single chunk
Text > 1000 chars  ──► split on sentence boundaries [.!?]
                        each chunk ≤ 1000 chars
                        last 150 chars overlap with next chunk
```

---

## Pipeline: Chat / Retrieval

Every user query passes through a 5-stage pipeline before receiving an answer.

### Stage 1: Query Rewriting

Generates 3 alternative phrasings of the user's question using **GPT-4o-mini** via Openrouter. This improves retrieval recall by searching for the same intent expressed differently.

**Example:**
- Input: *"How do I create an A/B test campaign?"*
- Output:
  - *"steps to set up an A/B test campaign"*
  - *"A/B campaign creation workflow"*
  - *"how to launch a split test experiment"*

### Stage 2: Hybrid Embedding

Each query (original + 3 rewrites) is encoded by **bge-m3** into:
- **Dense vector** (1024 floats) — captures semantic meaning
- **Sparse vector** (token → weight dict) — captures lexical/syntactic importance

### Stage 3: Hybrid Search (Qdrant)

Two parallel searches run against the Qdrant collection:
1. **Dense search** — cosine similarity on dense vectors (top 20)
2. **Sparse search** — sparse vector similarity (top 20)

Results are fused using **Reciprocal Rank Fusion (RRF)**:

```
score(d) = Σ 1 / (k + rank(d))
where k = 60 (smoothing constant)
```

### Stage 4: Cross-Encoder Reranking

The top RRF-fused results are scored by **bge-reranker-v2-m3** — a cross-encoder that evaluates each `(query, document)` pair as a whole, producing fine-grained relevance scores. The top 4 are kept.

### Stage 5: Generation

Two modes, auto-detected from the query:

**Answer mode** (questions like *"What is the purpose of..."*):
- Grounded Q&A using only retrieved context
- Answers cite chunks as `[Chunk N]`

**Generate mode** (phrases like *"create", "generate", "new test case", "VWO-1234"*):
- Produces a structured test case: Title, Preconditions, Steps, Expected, Priority, Tags
- Uses retrieved similar test cases as templates

---

## Project Structure

```
ADVANCE_RAG/
│
├── app.py                            # FastAPI backend — server, routes, orchestration
├── generate_testcases.py             # Generates 5,000 synthetic VWO test cases
├── requirements.txt                  # Python dependencies
├── .env                              # Environment config (API keys, paths)
│
├── modules/
│   ├── __init__.py                   # Package marker
│   ├── embedder.py                   # bge-m3 hybrid embedding (dense + sparse)
│   ├── ingest.py                     # CSV/XLSX → chunk → embed → index pipeline
│   ├── qdrant_ops.py                 # Qdrant vector DB operations
│   ├── reranker.py                   # bge-reranker-v2-m3 cross-encoder reranking
│   ├── rewriter.py                   # Query rewriting via Openrouter GPT-4o-mini
│   └── generator.py                  # Answer/test-case generation via Openrouter DeepSeek
│
├── static/
│   ├── index.html                    # Main chat UI (4 tabs, pipeline tracker)
│   └── explainer.html                # Interactive RAG explainer page with animations
│
├── prompt/
│   └── prompt.md                     # Original project specification
│
├── testcase/
│   └── vwo_test_cases.csv            # 5,000 generated test cases (optional, created by generate_testcases.py)
│
├── qdrant_data/                      # Local Qdrant embedded storage
│
└── uploads/                          # Uploaded files directory
```

---

## Components Deep Dive

### 1. Hybrid Embedder (bge-m3)

**File:** `modules/embedder.py`
**Model:** [`BAAI/bge-m3`](https://huggingface.co/BAAI/bge-m3) (~2.3 GB)

The embedder produces both dense and sparse vectors from a single forward pass:

- **Dense vector:** Mean pooling over `last_hidden_state` → 1024-dim float vector
- **Sparse vector:** ColBERT-style linear output → ReLU → bag-of-words `{token_id: weight}` dict

Key features:
- Singleton model loader (loaded once, reused across requests)
- CUDA support with automatic detection
- Batch processing (default batch size: 16)
- Fallback sparse computation if `sparse_logits` is unavailable

### 2. Vector Database (Qdrant)

**File:** `modules/qdrant_ops.py`
**Mode:** Embedded (no Docker required) or server mode

**Collection schema:**

| Component | Configuration |
|-----------|--------------|
| Dense vector `""` | 1024-dim, COSINE distance |
| Sparse vector `"sparse"` | Learned sparse index |
| Payload | `title`, `text`, `module`, `priority`, `jira_id`, `tags` |

Supports:
- Native hybrid search with `search_batch`
- Payload filtering by module/priority/tags
- Paginated scroll for chunk browsing

### 3. Cross-Encoder Reranker (bge-reranker-v2-m3)

**File:** `modules/reranker.py`
**Model:** [`BAAI/bge-reranker-v2-m3`](https://huggingface.co/BAAI/bge-reranker-v2-m3) (~570 MB)

Unlike bi-encoders (which pre-compute embeddings), cross-encoders process each `(query, document)` pair together through the full transformer, producing highly accurate relevance scores. Used as the final ranking stage before LLM generation.

### 4. Query Rewriter (GPT-4o-mini)

**File:** `modules/rewriter.py`
**Model:** `openai/gpt-4o-mini` via Openrouter

Generates 3 diverse phrasings of the user's query to maximize retrieval coverage. Falls back to the original query if the API call fails.

### 5. Answer Generator (DeepSeek Chat)

**File:** `modules/generator.py`
**Model:** `deepseek/deepseek-chat` via Openrouter

Two system prompts control behavior:
- **Answer mode:** Strictly grounded — uses only provided context with `[Chunk N]` citations
- **Generate mode:** Structured output — produces a complete test case spec

Falls back to a formatted list of chunks if no API key is configured.

---

## API Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| `GET` | `/` | Serve main chat UI (`index.html`) |
| `GET` | `/explainer` | Serve architecture explainer page (`explainer.html`) |
| `POST` | `/api/upload` | Upload a CSV/XLSX file (returns preview + filepath) |
| `POST` | `/api/ingest/start` | Start ingestion pipeline for an uploaded file |
| `GET` | `/api/ingest/stream/{task_id}` | SSE progress stream for ingestion |
| `POST` | `/api/ingest/file` | Direct file ingestion (single endpoint) |
| `POST` | `/api/chat` | Full RAG pipeline — send query, get answer |
| `GET` | `/api/chunks` | Paginated chunk viewer with search + filters |
| `GET` | `/api/collection/info` | Qdrant collection metadata |

### Chat API Request

```json
POST /api/chat
{
  "message": "How do I create an A/B test campaign?"
}
```

### Chat API Response

```json
{
  "query": "How do I create an A/B test campaign?",
  "rewrites": [
    "steps to set up an A/B test campaign",
    "A/B campaign creation workflow",
    "how to launch a split test experiment"
  ],
  "hybrid_results": [...],
  "reranked_results": [...],
  "answer": "Based on the test cases found, creating an A/B campaign involves...\n\n[Chunk 1] Navigate to Campaigns > Create New\n[Chunk 2] Select A/B test type...",
  "model": "deepseek/deepseek-chat",
  "is_generate": false
}
```

---

## Frontend UI

### Main UI (`static/index.html`)

A single-page application with a Claude-inspired theme (warm cream + coral) and 4 tabs:

| Tab | Feature |
|-----|---------|
| **Upload** | Drag-drop CSV/XLSX upload with preview (columns, first 5 rows, dtypes) |
| **Ingest** | Live 5-stage pipeline progress tracker |
| **Chunks** | Paginated chunk browser with search and filter by module/priority |
| **Chat** | Two-pane layout: left = pipeline stage tracker, right = chat messages |

Chat features:
- Stage-by-stage visual progress (pending → active → completed)
- Query rewrites displayed as bubbles
- Top reranked results shown with scores
- Final answer with model attribution
- Auto-detected generate mode (coral outline)

### Explainer Page (`static/explainer.html`)

A standalone educational page covering:
- RAG concept explanation with diagrams
- System architecture (Ingest + Chat pipelines)
- Component deep-dive accordion panels
- Animated data flow visualization
- Complete setup and configuration reference

---

## Configuration & Tunables

### Environment Variables (`.env`)

| Variable | Default | Purpose |
|----------|---------|---------|
| `OPENROUTER_API_KEY` | — | API key for Openrouter LLM calls |
| `QDRANT_PATH` | `./qdrant_data` | Local embedded Qdrant storage path |
| `COLLECTION_NAME` | `vwo_test_cases` | Qdrant collection name |
| `PORT` | `5050` | FastAPI server port |

### Pipeline Tunables (in `app.py`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `CHUNK_SIZE` | 1000 | Max characters per chunk before splitting |
| `CHUNK_OVERLAP` | 150 | Character overlap between adjacent chunks |
| `TOP_N_HYBRID` | 20 | Candidates per dense/sparse search |
| `TOP_K_RERANK` | 4 | Final chunks sent to LLM after reranking |
| `RRF_K` | 60 | RRF smoothing constant |
| `REWRITE_ENABLED` | True | Enable query rewriting via Openrouter |

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- pip

### Steps

```bash
# Clone or navigate to the project
cd ADVANCE_RAG

# Create and activate a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx
QDRANT_PATH=./qdrant_data
COLLECTION_NAME=vwo_test_cases
PORT=5050
```

Get an API key from [Openrouter](https://openrouter.ai/).

---

## Running the Application

### Start the Server

```bash
python app.py
```

Open **http://127.0.0.1:5050** in your browser.

### Quick Start Workflow

1. Go to the **Upload** tab and upload `testcase/vwo_test_cases.csv` (or generate it first — see below)
2. Select text columns and metadata columns
3. Click **Ingest** and watch the 5-stage pipeline progress
4. Switch to the **Chat** tab and start asking questions

### Generating Test Data

```bash
python generate_testcases.py
```

This creates `testcase/vwo_test_cases.csv` with 5,000 synthetic VWO test cases across 10 modules (Campaign Management, User Segmentation, Reporting, Integrations, Account Settings, User Management, Billing, API & Webhooks, Audience Targeting, Personalization).

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **First query is slow** | bge-m3 (~2.3 GB) and bge-reranker (~570 MB) download on first use from HuggingFace. Subsequent requests are fast. |
| **Openrouter 401** | Check `OPENROUTER_API_KEY` in `.env` |
| **Out of memory** | Set `INGEST_BATCH=16` (or lower) in the embedder. Models run in FP16 by default. |
| **Port 5050 busy** | Change `PORT` in `.env` |
| **No CSV data** | Run `python generate_testcases.py` first |
| **Qdrant locked** | Delete `qdrant_data/.lock` and restart |

---

## Tech Stack Summary

| Component | Technology | Size / Scale |
|-----------|-----------|-------------|
| **Backend** | FastAPI + Uvicorn | Single process, async |
| **Embeddings** | BAAI/bge-m3 | ~2.3 GB, 1024-dim dense + sparse |
| **Reranker** | BAAI/bge-reranker-v2-m3 | ~570 MB cross-encoder |
| **Vector DB** | Qdrant (embedded) | File-based, no Docker |
| **LLM (Rewrite)** | GPT-4o-mini via Openrouter | 3 query rewrites per request |
| **LLM (Generate)** | DeepSeek Chat via Openrouter | Grounded Q&A or test case gen |
| **Frontend** | Vanilla HTML / CSS / JS | Claude-inspired theme, SPA |
| **Data** | 5,000 VWO test cases | 10 modules, ~2.4 MB CSV |
| **Documentation** | Interactive HTML explainer | Animated architecture diagrams |

---

## License

This project is created for educational purposes as part of **The Testing Academy** training curriculum.