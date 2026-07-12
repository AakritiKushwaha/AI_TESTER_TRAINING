"""Document ingestion pipeline: parse, chunk, embed, index."""

import os
import re
import math
import logging
from typing import Optional
from io import StringIO

import pandas as pd

from modules.embedder import embed, dense_dim
from modules.qdrant_ops import index_documents, ensure_collection

logger = logging.getLogger(__name__)

# Tunables
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def load_file(filepath: str) -> pd.DataFrame:
    """Load CSV or XLSX into a DataFrame."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".csv":
        return pd.read_csv(filepath)
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def load_dataframe_from_text(content: str, filename: str) -> pd.DataFrame:
    """Load CSV/XLSX content from raw text (for uploaded files via FastAPI)."""
    if filename.endswith(".csv"):
        return pd.read_csv(StringIO(content))
    else:
        raise ValueError("Only CSV text uploads supported. Use file upload for XLSX.")


def assemble_documents(df: pd.DataFrame, text_cols: list[str], meta_cols: list[str]) -> list[dict]:
    """Convert DataFrame rows to document dicts with combined text and metadata."""
    docs = []
    for _, row in df.iterrows():
        # Combine text columns into a single document text
        text_parts = []
        for col in text_cols:
            val = row.get(col, "")
            if pd.notna(val):
                text_parts.append(f"{col}: {val}")
        doc_text = "\n".join(text_parts)

        # Build metadata
        meta = {}
        for col in meta_cols:
            val = row.get(col, "")
            meta[col] = str(val) if pd.notna(val) else ""

        docs.append({
            "text": doc_text,
            "title": str(row.get(text_cols[0], "")) if text_cols else "",
            "module": meta.get("module", ""),
            "priority": meta.get("priority", ""),
            "jira_id": meta.get("jira_id", ""),
            "tags": meta.get("tags", ""),
            "id": int(row.get("id", 0)) if "id" in row else 0,
        })
    return docs


def chunk_documents(docs: list[dict]) -> list[dict]:
    """Split long documents into chunks with overlap."""
    chunks = []
    for doc in docs:
        text = doc.get("text", "")
        if len(text) <= CHUNK_SIZE:
            doc["chunk_index"] = 0
            chunks.append(doc)
            continue

        # Split into sentences first
        sentences = re.split(r"(?<=[.!?])\s+", text)
        current_chunk = ""
        chunk_idx = 0

        for sent in sentences:
            if len(current_chunk) + len(sent) > CHUNK_SIZE and current_chunk:
                chunk = dict(doc)
                chunk["text"] = current_chunk.strip()
                chunk["chunk_index"] = chunk_idx
                chunks.append(chunk)
                chunk_idx += 1
                # Overlap: keep last CHUNK_OVERLAP chars
                overlap_text = current_chunk[-CHUNK_OVERLAP:] if len(current_chunk) > CHUNK_OVERLAP else ""
                current_chunk = overlap_text + " " + sent
            else:
                if current_chunk:
                    current_chunk += " " + sent
                else:
                    current_chunk = sent

        if current_chunk.strip():
            chunk = dict(doc)
            chunk["text"] = current_chunk.strip()
            chunk["chunk_index"] = chunk_idx
            chunks.append(chunk)

    return chunks


def ingest_pipeline(
    df: pd.DataFrame,
    text_cols: list[str],
    meta_cols: list[str],
    progress_callback=None,
) -> dict:
    """Run the full ingest pipeline and return stats."""
    stats = {}

    def _progress(stage: str, data: dict = None):
        if progress_callback:
            progress_callback(stage, data or {})

    # 1. Build docs
    _progress("read", {"rows": len(df), "columns": list(df.columns)})
    docs = assemble_documents(df, text_cols, meta_cols)
    _progress("build_docs", {"doc_count": len(docs)})

    # 2. Chunk
    chunks = chunk_documents(docs)
    chunk_stats = _chunk_statistics(chunks)
    _progress("chunk", chunk_stats)

    # 3. Embed
    texts = [c["text"] for c in chunks]
    batch_size = 16
    all_dense = []
    all_sparse = []
    total = len(texts)
    for i in range(0, total, batch_size):
        batch = texts[i : i + batch_size]
        dense, sparse = embed(batch, batch_size=batch_size)
        all_dense.extend(dense)
        all_sparse.extend(sparse)
        _progress("embed", {
            "current": min(i + batch_size, total),
            "total": total,
            "dense_dim": len(dense[0]) if dense else 0,
        })

    # 4. Index into Qdrant
    ensure_collection(dense_dim=dense_dim())
    for chunk in chunks:
        chunk["id"] = abs(hash(chunk.get("text", ""))) % (2**63)

    ids = [abs(hash(c.get("text", ""))) % (2**63) for c in chunks]
    for c, cid in zip(chunks, ids):
        c["id"] = cid

    index_documents(chunks, all_dense, all_sparse, batch_size=64)
    _progress("index", {"total_points": len(chunks)})

    return {
        "chunks": chunk_stats,
        "total_chunks": len(chunks),
        "total_docs": len(docs),
    }


def _chunk_statistics(chunks: list[dict]) -> dict:
    lengths = [len(c.get("text", "")) for c in chunks]
    if not lengths:
        return {"count": 0}
    return {
        "count": len(lengths),
        "avg_chars": round(sum(lengths) / len(lengths), 1),
        "min_chars": min(lengths),
        "max_chars": max(lengths),
        "sample_chunks": [c.get("text", "")[:200] for c in chunks[:5]],
    }
