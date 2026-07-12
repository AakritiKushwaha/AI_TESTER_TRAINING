"""Qdrant vector DB operations for dense + sparse hybrid search."""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    SparseVectorParams,
    SparseIndexParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchText,
    SearchRequest,
    NamedVector,
    NamedSparseVector,
    QuantizationSearchParams,
)

load_dotenv()
logger = logging.getLogger(__name__)

_client: Optional[QdrantClient] = None
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "vwo_test_cases")


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        qdrant_path = os.getenv("QDRANT_PATH", "./qdrant_data")
        url = os.getenv("QDRANT_URL", "")
        if url:
            _client = QdrantClient(url=url)
            logger.info(f"Connected to Qdrant server at {url}")
        else:
            _client = QdrantClient(path=qdrant_path)
            logger.info(f"Using embedded Qdrant at {qdrant_path}")
    return _client


def ensure_collection(dense_dim: int = 1024):
    """Create collection if it doesn't exist, with dense + sparse vector config."""
    client = get_client()
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in collections:
        logger.info(f"Collection '{COLLECTION_NAME}' already exists.")
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=dense_dim, distance=Distance.COSINE),
        sparse_vectors_config=SparseVectorParams(
            index=SparseIndexParams(on_disk=False)
        ),
    )
    logger.info(f"Created collection '{COLLECTION_NAME}' with dense + sparse config.")


def index_documents(
    docs: list[dict],
    dense_vectors: list[list[float]],
    sparse_vectors: list[dict],
    batch_size: int = 64,
):
    """Index documents with their dense and sparse vectors."""
    client = get_client()
    ensure_collection(dense_dim=len(dense_vectors[0]) if dense_vectors else 1024)

    points = []
    for i, doc in enumerate(docs):
        points.append(
            PointStruct(
                id=doc.get("id", i + 1),
                vector={
                    "": dense_vectors[i],
                    "sparse": sparse_vectors[i],
                },
                payload={
                    "title": doc.get("title", ""),
                    "text": doc.get("text", ""),
                    "module": doc.get("module", ""),
                    "priority": doc.get("priority", ""),
                    "jira_id": doc.get("jira_id", ""),
                    "tags": doc.get("tags", ""),
                },
            )
        )

        if len(points) >= batch_size:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            points = []

    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)

    counts = client.count(collection_name=COLLECTION_NAME)
    logger.info(f"Indexed documents. Total points: {counts.count}")


def hybrid_search(
    dense_vector: list[float],
    sparse_vector: dict,
    top_n: int = 20,
    filters: Optional[dict] = None,
) -> list[dict]:
    """Search using dense + sparse with RRF fusion built into Qdrant."""
    client = get_client()
    search_filter = None
    if filters:
        conditions = []
        for key, value in filters.items():
            if isinstance(value, str):
                conditions.append(FieldCondition(key=key, match=MatchText(text=value)))
            else:
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
        search_filter = Filter(must=conditions)

    # Qdrant's native hybrid search with prefetch
    results = client.search_batch(
        collection_name=COLLECTION_NAME,
        requests=[
            SearchRequest(
                vector=NamedVector(name="", vector=dense_vector),
                limit=top_n,
                score_threshold=0.0,
                filter=search_filter,
                params=QuantizationSearchParams(ignore=False),
            ),
            SearchRequest(
                vector=NamedSparseVector(name="sparse", vector=sparse_vector),
                limit=top_n,
                score_threshold=0.0,
                filter=search_filter,
            ),
        ],
    )

    # results is a list of 2 lists of ScoredPoint
    dense_hits = results[0]
    sparse_hits = results[1]

    # RRF fusion
    rrf_k = 60
    scores: dict[int, float] = {}
    payloads: dict[int, dict] = {}

    for rank, hit in enumerate(dense_hits):
        scores[hit.id] = scores.get(hit.id, 0) + 1.0 / (rrf_k + rank)
        payloads[hit.id] = hit.payload or {}

    for rank, hit in enumerate(sparse_hits):
        scores[hit.id] = scores.get(hit.id, 0) + 1.0 / (rrf_k + rank)
        if hit.id not in payloads:
            payloads[hit.id] = hit.payload or {}

    # Sort by RRF score descending
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    results_out = []
    for point_id, score in ranked:
        p = payloads.get(point_id, {})
        results_out.append({
            "id": point_id,
            "score": round(score, 4),
            "title": p.get("title", ""),
            "text": p.get("text", ""),
            "module": p.get("module", ""),
            "priority": p.get("priority", ""),
            "jira_id": p.get("jira_id", ""),
            "tags": p.get("tags", ""),
        })

    return results_out


def scroll_all(limit: int = 100, offset: Optional[int] = None):
    """Paginated scroll over all points in the collection."""
    client = get_client()
    records, next_offset = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=limit,
        offset=offset,
        with_payload=True,
        with_vectors=False,
    )
    results = []
    for rec in records:
        p = rec.payload or {}
        results.append({
            "id": rec.id,
            "title": p.get("title", ""),
            "text": p.get("text", ""),
            "module": p.get("module", ""),
            "priority": p.get("priority", ""),
            "jira_id": p.get("jira_id", ""),
            "tags": p.get("tags", ""),
        })
    return results, next_offset


def collection_info() -> dict:
    client = get_client()
    info = client.get_collection(collection_name=COLLECTION_NAME)
    return {
        "name": COLLECTION_NAME,
        "points_count": info.points_count,
        "vectors_count": info.vectors_count,
        "status": str(info.status),
    }
