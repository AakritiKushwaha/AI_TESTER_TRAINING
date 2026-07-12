"""Advanced RAG Explorer — FastAPI backend with Claude-inspired UI."""

import os
import json
import asyncio
import logging
from io import StringIO
from typing import Optional
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from modules.ingest import ingest_pipeline, load_file, chunk_documents, assemble_documents
from modules.embedder import embed_query
from modules.qdrant_ops import hybrid_search, scroll_all, collection_info
from modules.reranker import rerank
from modules.rewriter import rewrite_query
from modules.generator import generate

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Tunables
TOP_N_HYBRID = 20
TOP_K_RERANK = 4
RRF_K = 60
REWRITE_ENABLED = True

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# FastAPI lifecycle
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Advanced RAG Explorer starting up...")
    yield
    logger.info("Shutting down.")

app = FastAPI(title="Advanced RAG Explorer", lifespan=lifespan)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index():
    return serve_frontend("index.html")


@app.get("/explainer", response_class=HTMLResponse)
async def explainer():
    return serve_frontend("explainer.html")


# ---- Upload ----
@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...)):
    """Upload a CSV/XLSX file, return preview info."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".csv", ".xlsx", ".xls"):
        raise HTTPException(400, "Only .csv, .xlsx, .xls files supported")

    content = await file.read()
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        f.write(content)

    if ext == ".csv":
        df = pd.read_csv(StringIO(content.decode("utf-8")))
    else:
        with open(filepath, "rb") as f:
            df = pd.read_excel(f)

    return {
        "filename": file.filename,
        "rows": len(df),
        "columns": list(df.columns),
        "dtypes": {c: str(df[c].dtype) for c in df.columns},
        "preview": df.head(5).fillna("").to_dict(orient="records"),
        "filepath": filepath,
    }


# ---- Ingest (SSE) ----
@app.post("/api/ingest/start")
async def api_ingest_start(
    filepath: str = Form(...),
    text_cols: str = Form("title,steps,expected"),
    meta_cols: str = Form("id,jira_id,priority,module,tags"),
):
    """Start ingestion in background and return a task id."""
    text_cols_list = [c.strip() for c in text_cols.split(",")]
    meta_cols_list = [c.strip() for c in meta_cols.split(",")]

    df = load_file(filepath)

    # We run sync code in a thread to not block
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, lambda: ingest_pipeline(df, text_cols_list, meta_cols_list)
    )
    return result


@app.get("/api/ingest/stream/{task_id}")
async def api_ingest_stream(task_id: str):
    """SSE stream for ingestion progress (simplified: we just return final)."""
    pass  # Placeholder — we handle SSE inline in the frontend logic


# ---- Chunks ----
@app.get("/api/chunks")
async def api_chunks(
    limit: int = Query(50),
    offset: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
):
    """Paginated chunk viewer with filters."""
    results, next_offset = scroll_all(limit=limit, offset=offset)
    info = collection_info()

    # Simple server-side filter (since Qdrant scroll doesn't filter)
    if module:
        results = [r for r in results if r.get("module", "").lower() == module.lower()]
    if priority:
        results = [r for r in results if r.get("priority", "").lower() == priority.lower()]
    if search:
        search_lower = search.lower()
        results = [
            r
            for r in results
            if search_lower in r.get("title", "").lower()
            or search_lower in r.get("text", "").lower()
            or search_lower in r.get("jira_id", "").lower()
        ]

    return {
        "points": results,
        "total": info["points_count"],
        "next_offset": next_offset,
    }


@app.get("/api/collection/info")
async def api_collection_info():
    return collection_info()


# ---- Chat ----
@app.post("/api/chat")
async def api_chat(data: dict):
    """Full RAG pipeline: rewrite -> embed -> hybrid search -> rerank -> generate."""
    query = data.get("message", "").strip()
    if not query:
        raise HTTPException(400, "Message is required")

    is_generate = _detect_generate_mode(query)

    # 1. Rewrite
    rewrites = [query]
    if REWRITE_ENABLED:
        try:
            rewrites = rewrite_query(query)
        except Exception as e:
            logger.warning(f"Rewrite failed: {e}")
            rewrites = [query]

    # 2. Embed all query variants
    all_dense_hits = []
    all_sparse_hits = []
    for rq in rewrites:
        dense_vec, sparse_dict = embed_query(rq)
        hits = hybrid_search(dense_vec, sparse_dict, top_n=TOP_N_HYBRID)
        all_dense_hits.extend(hits)

    # Deduplicate by id after hybrid search
    seen_ids = set()
    fused = []
    for hit in all_dense_hits:
        if hit["id"] not in seen_ids:
            seen_ids.add(hit["id"])
            fused.append(hit)

    # Sort by score descending
    fused.sort(key=lambda x: -x["score"])
    fused = fused[:TOP_N_HYBRID * 2]

    # 3. Rerank
    reranked = rerank(query, fused, top_k=TOP_K_RERANK)

    # 4. Generate
    answer, model_used = generate(query, reranked, is_generate_mode=is_generate)

    return {
        "query": query,
        "rewrites": rewrites,
        "dense_top_n": TOP_N_HYBRID,
        "sparse_top_n": TOP_N_HYBRID,
        "rrf_k": RRF_K,
        "rerank_top_k": TOP_K_RERANK,
        "hybrid_results": fused[:10],  # top 10 for display
        "reranked_results": reranked,
        "answer": answer,
        "model": model_used,
        "is_generate": is_generate,
    }


def _detect_generate_mode(query: str) -> bool:
    """Auto-detect if user wants to generate a test case vs ask a question."""
    generate_phrases = [
        "create", "generate", "new test case", "write a test", "make a test",
        "draft", "produce", "VWO-", "jira",
    ]
    q = query.lower()
    return any(phrase in q for phrase in generate_phrases)


# ---- Ingest file directly (CLI-style) ----
@app.post("/api/ingest/file")
async def api_ingest_file(
    filepath: str = Form(...),
    text_cols: str = Form("title,steps,expected"),
    meta_cols: str = Form("id,jira_id,priority,module,tags"),
):
    """Ingest a file directly (for the pre-generated CSV)."""
    text_cols_list = [c.strip() for c in text_cols.split(",")]
    meta_cols_list = [c.strip() for c in meta_cols.split(",")]
    df = load_file(filepath)
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, lambda: ingest_pipeline(df, text_cols_list, meta_cols_list)
    )
    return result


# ---------------------------------------------------------------------------
# HTML frontend (inline)
# ---------------------------------------------------------------------------
def serve_frontend(page: str) -> str:
    """Return the HTML for the requested page."""
    page_path = os.path.join(STATIC_DIR, page)
    if os.path.exists(page_path):
        with open(page_path, "r", encoding="utf-8") as f:
            return f.read()

    # Fallback: return the main page
    if page == "index.html":
        return _main_html()
    return _main_html()


FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(FRONTEND_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    port = int(os.getenv("PORT", "5050"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
