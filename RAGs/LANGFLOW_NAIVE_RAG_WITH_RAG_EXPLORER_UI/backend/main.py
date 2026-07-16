import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

# Load .env from the project root (one level up from backend/)
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path, override=True)

LANGFLOW_URL = os.getenv("LANGFLOW_URL", "").strip().rstrip("/")
LANGFLOW_FLOW_ID = os.getenv("LANGFLOW_FLOW_ID", "").strip()
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "").strip()

LANGFLOW_HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": LANGFLOW_API_KEY,
} if LANGFLOW_API_KEY else {}

app = FastAPI(title="RAG Explorer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    chunks: list[dict]
    model: str | None = None
    tokens: int | None = None


def _build_langflow_payload(question: str) -> dict:
    return {
        "input_value": question,
        "input_type": "chat",
        "output_type": "chat",
    }


def _build_langflow_headers() -> dict:
    return {
        "Content-Type": "application/json",
        "x-api-key": LANGFLOW_API_KEY,
    }


def _extract_outputs(response_json: dict) -> list[dict]:
    """Extract the list of output dicts from a Langflow response."""
    outputs = response_json.get("outputs") or []
    flat = []
    for o in outputs:
        inner = o.get("outputs") or []
        flat.extend(inner)
    return flat


def _extract_answer(flat_outputs: list[dict]) -> str | None:
    """Walk outputs looking for the chat message result text."""
    for out in flat_outputs:
        results = out.get("results") or {}
        if not isinstance(results, dict):
            continue
        msg = results.get("message") or {}
        if isinstance(msg, dict):
            data = msg.get("data") or {}
            if isinstance(data, dict):
                text = data.get("text")
                if text and isinstance(text, str) and text.strip():
                    return text
        # fallback: raw text/result field on the output itself
        text = out.get("text") or results.get("text") or results.get("result")
        if isinstance(text, str) and text.strip():
            return text
    return None


_METADATA_KEYS = frozenset({
    "sender", "sender_name", "type", "files", "session_id", "context_id",
    "error", "edit", "run_id", "flow_id", "timestamp", "category",
    "content_blocks", "component_id", "component_display_name",
    "used_frozen_result", "token_usage", "timedelta", "duration",
    "stream_url", "default_value", "text_key",
})


def _extract_chunks(flat_outputs: list[dict]) -> list[dict]:
    """
    Walk outputs looking for non-chat component text results
    (e.g. Parse Data, Chroma DB outputs from intermediate nodes).

    Langflow only exposes intermediate component outputs when the Chat Output
    has 'additional outputs' configured. Otherwise only the final answer is
    available, and this will return an empty list.
    """
    chunks: list[dict] = []
    for out in flat_outputs:
        results = out.get("results") or {}
        if not isinstance(results, dict):
            continue
        for comp_key, comp_val in results.items():
            if comp_key in _METADATA_KEYS or comp_key == "message":
                continue
            if isinstance(comp_val, dict):
                text = (
                    comp_val.get("text")
                    or comp_val.get("result")
                    or (comp_val.get("data") or {}).get("text")
                )
                if text and isinstance(text, str) and text.strip() and len(text) > 30:
                    chunks.append({"source": comp_key, "text": text.strip()})
    return chunks


def _extract_metadata(flat_outputs: list[dict]) -> tuple[str | None, int | None]:
    """Extract model name and token count from the Langflow response."""
    model = None
    tokens = None
    for out in flat_outputs:
        results = out.get("results") or {}
        if not isinstance(results, dict):
            continue
        msg = results.get("message") or {}
        if isinstance(msg, dict):
            data = msg.get("data") or {}
            if isinstance(data, dict):
                # model is inside properties.source.source
                props = data.get("properties") or {}
                if isinstance(props, dict):
                    source = props.get("source") or {}
                    if isinstance(source, dict):
                        model = source.get("source") or model
                    usage = props.get("usage") or {}
                    if isinstance(usage, dict):
                        tokens = usage.get("total_tokens") or tokens
    return model, tokens


router = APIRouter(prefix="/api")


@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    if not LANGFLOW_URL or not LANGFLOW_FLOW_ID:
        raise HTTPException(
            status_code=500, detail="Langflow is not configured in .env"
        )

    url = f"{LANGFLOW_URL}/api/v1/run/{LANGFLOW_FLOW_ID}"
    payload = _build_langflow_payload(req.question)
    headers = _build_langflow_headers()

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        detail = f"Langflow returned HTTP {e.response.status_code}: {e.response.text[:500]}"
        raise HTTPException(status_code=502, detail=detail)
    except httpx.RequestError as e:
        detail = f"Cannot reach Langflow at {LANGFLOW_URL}: {e}"
        raise HTTPException(status_code=502, detail=detail)

    flat = _extract_outputs(data)
    answer = _extract_answer(flat) or "No answer returned from Langflow."
    chunks = _extract_chunks(flat)
    model, tokens = _extract_metadata(flat)

    return AskResponse(answer=answer, chunks=chunks, model=model, tokens=tokens)


@router.get("/test-connection")
async def test_connection():
    if not LANGFLOW_URL or not LANGFLOW_FLOW_ID:
        raise HTTPException(
            status_code=500, detail="Langflow is not configured in .env"
        )

    url = f"{LANGFLOW_URL}/api/v1/run/{LANGFLOW_FLOW_ID}"
    payload = _build_langflow_payload("ping")
    headers = _build_langflow_headers()

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return {"status": "ok", "flow_id": LANGFLOW_FLOW_ID}
    except Exception as e:
        return {"status": "error", "detail": str(e), "flow_id": LANGFLOW_FLOW_ID}


@app.get("/")
async def root():
    return {"app": "RAG Explorer API", "status": "running"}


# ── Pipeline Status ─────────────────────────────────────────────────


def _run_lightweight_check() -> dict:
    """Execute the existing Langlow flow with a trivial input to verify it works.

    Sends a non-generative trigger to the Langflow run API so the Chroma
    component executes and returns metadata through the pipeline. No local
    disk access — purely through the Langflow API, which means this works
    even when Langflow is remote (Docker, different host, etc.).

    Returns a dict with Chroma runtime info if the call succeeds, or an
    error dict if Langflow is unreachable.
    """
    url = f"{LANGFLOW_URL}/api/v1/run/{LANGFLOW_FLOW_ID}"
    payload = _build_langflow_payload("status")
    headers = _build_langflow_headers()

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except httpx.RequestError as exc:
        return {
            "connected": False,
            "error": f"Cannot reach Langflow at {LANGFLOW_URL}: {exc}",
        }
    except httpx.HTTPStatusError as exc:
        return {
            "connected": False,
            "error": f"Langflow returned HTTP {exc.response.status_code}: {exc.response.text[:500]}",
        }

    # Walk intermediate component outputs looking for Chroma results
    flat = _extract_outputs(data)
    doc_count = None
    embedding_dims = None

    for out in flat:
        results = out.get("results") or {}
        if not isinstance(results, dict):
            continue
        for comp_key, comp_val in results.items():
            if comp_key in _METADATA_KEYS or comp_key == "message":
                continue
            if not isinstance(comp_val, dict):
                continue

            inner_data = comp_val.get("data") or {}
            if not isinstance(inner_data, dict):
                inner_data = {}

            # Try to extract items array (Langflow component output style)
            items = inner_data.get("items") or comp_val.get("items") or []
            if isinstance(items, list) and len(items) > 0:
                doc_count = len(items)
                # Check first item for embedding dimensions
                first = items[0]
                if isinstance(first, dict):
                    emb = first.get("embedding") or first.get("vector")
                    if isinstance(emb, (list, tuple)):
                        embedding_dims = len(emb)

            # Fallback: count document-like entries in text field
            if doc_count is None:
                text = (
                    inner_data.get("text")
                    or comp_val.get("text")
                    or comp_val.get("result")
                    or ""
                )
                if isinstance(text, str) and len(text) > 100:
                    # Chroma returns documents separated by the source key pattern
                    doc_count = text.count("source:") or text.count("【")

    return {
        "connected": True,
        "total_vectors_stored": doc_count,
        "embedding_dims": embedding_dims,
    }


def _fetch_flow_config() -> tuple[dict | None, str | None]:
    """Fetch Langlow flow definition and return extracted Chroma config.

    Returns ``(config_dict, error_str)`` — one is ``None``.
    """
    url = f"{LANGFLOW_URL}/api/v1/flows/{LANGFLOW_FLOW_ID}"
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=LANGFLOW_HEADERS)
            resp.raise_for_status()
            flow = resp.json()
    except Exception as exc:
        return None, str(exc)

    nodes = (
        flow.get("data", {}).get("nodes", [])
        if isinstance(flow, dict)
        else []
    )
    info: dict = {}
    for n in nodes:
        nd = n.get("data", {}).get("node", {})
        tpl = nd.get("template", {})
        name = nd.get("display_name", "").lower()
        if "chroma" in name:
            for k in ("collection_name", "persist_directory", "number_of_results"):
                v = tpl.get(k, {})
                if isinstance(v, dict) and v.get("value"):
                    info[k] = v["value"]
        if "mistral" in name or "embed" in name:
            for k in ("model",):
                v = tpl.get(k, {})
                if isinstance(v, dict) and v.get("value"):
                    info[f"embedding_{k}"] = v["value"]
    return info if info else None, None


@router.get("/pipeline-status")
async def pipeline_status():
    """
    Return live Langflow & Chroma DB pipeline metadata.

    - ``connected`` reflects whether the Langflow API is reachable and the
      flow executed successfully.
    - Chroma collection details are obtained by *running* the Langflow
      flow with a lightweight trigger — no local disk access required.
    - Static config (collection_name, embedding_model) comes from the flow
      definition as a fallback.
    """
    # Step 1: Verify the pipeline can actually run (lightweight call)
    run_result = _run_lightweight_check()

    if not run_result.get("connected"):
        return {
            "connected": False,
            "error": run_result.get("error", "Pipeline check failed"),
            "last_checked": datetime.now(timezone.utc).isoformat(),
        }

    # Step 2: Get static config from the flow definition
    flow_config, config_err = _fetch_flow_config()
    collection_name = (
        flow_config.get("collection_name", "ecom_test_cases")
        if flow_config
        else "ecom_test_cases"
    )
    embedding_model = (flow_config or {}).get("embedding_model")

    # Step 3: Merge runtime data from the lightweight run with config
    return {
        "connected": True,
        "collection_name": collection_name,
        "total_vectors_stored": run_result.get("total_vectors_stored"),
        "embedding_dims": run_result.get("embedding_dims") or (
            flow_config.get("embedding_dimensions") if flow_config else None
        ),
        "embedding_model": embedding_model,
        "last_checked": datetime.now(timezone.utc).isoformat(),
    }
