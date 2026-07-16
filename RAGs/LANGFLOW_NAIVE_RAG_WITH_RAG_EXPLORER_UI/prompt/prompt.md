# RAG Explorer — Project Prompt (Langflow-Connected)

Build a simple RAG (Retrieval-Augmented Generation) Explorer as a lightweight React + Vite web application. The goal is to make the RAG mechanism transparent and explorable, not just a black-box chatbot.

This RAG Explorer does **not** implement its own ingestion/retrieval/generation logic. Instead, it acts as a custom frontend UI that calls a **Langflow flow** (already built separately) via Langflow's REST API. The FastAPI backend is a thin proxy layer between the React frontend and Langflow.

## Data Source
- A CSV file will be provided in the `/data` folder — it's a set of 1000 e-commerce test cases (`ecom_test_cases.csv`), covering 10 modules (Login, Registration, Product Search & Listing, Product Details, Add to Cart, Wishlist, Checkout, Payment, Order Management, User Profile & Account Settings).
- Ingestion of this file happens inside **Langflow** (Read File → Split Text → Mistral Embeddings → Chroma DB), not inside this app.

## Backend Responsibilities (FastAPI proxy)

### 1. `POST /ask`
- Accepts `{ "question": "<user query>" }`.
- Forwards the request to the Langflow flow's REST API:
POST {LANGFLOW_URL}/api/v1/run/{LANGFLOW_FLOW_ID}
Headers: Content-Type: application/json, x-api-key: {LANGFLOW_API_KEY}
Body: { "input_value": "<question>", "input_type": "chat", "output_type": "chat" }

- Parses the Langflow response and returns to the frontend:
  - The final generated answer text.
  - The retrieved chunks (from the Chroma DB / Parser component's output, exposed via a second output component in the flow) — including which test case(s) each chunk came from, so the UI can show "top-4 retrieved" transparency.

### 2. `GET /pipeline-status` (live status, not hardcoded)
This endpoint returns the *live*, current state of the Langflow-backed RAG pipeline:
1. Call the Langflow flow with a lightweight, non-generative trigger request (e.g., an empty/trivial `input_value`, or a dedicated status-check flow/component) that causes the Chroma DB component to return collection metadata (e.g., item count) rather than triggering full LLM generation.
   - If the main flow doesn't cleanly support this, add a **second, minimal Langflow flow** dedicated to status-checking: Chroma DB component alone, connected to a Chat/Text Output, returning `collection_name`, item count, and embedding dimensions — no chunking/embedding/LLM steps involved.
2. Parse the response into a normalized shape:
```json
   {
     "connected": true,
     "collection_name": "ecom_test_cases",
     "total_vectors_stored": 1000,
     "embedding_dims": 1024,
     "last_checked": "<ISO timestamp>"
   }
```
3. If the Langflow call fails (timeout, auth error, connection refused), return `{"connected": false, "error": "<reason>"}` instead of throwing.
4. Called by the frontend on page load and on-demand via a "Test Connection" / "Refresh Status" button — no continuous polling by default.

### 3. Environment variables
Read `LANGFLOW_URL`, `LANGFLOW_FLOW_ID`, and `LANGFLOW_API_KEY` from a `.env` file — never hardcode these.

## Tech Stack Summary
| Component | Tool |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI (thin proxy only — no direct ChromaDB/embedding/LLM calls) |
| Orchestration Engine | Langflow (runs ingestion + retrieval + generation) |
| Embedding Model | Mistral Embeddings (`mistral-embed`), configured inside Langflow |
| Vector Store | ChromaDB — embedded/persistent client, on-disk (`./chroma_data`), configured inside Langflow |
| LLM Provider | Groq API, configured inside Langflow |

## Constraints
- This app must **not** duplicate RAG logic (no direct ChromaDB client, no direct embedding calls, no direct Groq calls in this codebase) — all of that lives in the Langflow flow.
- All Langflow connection details (URL, flow ID, API key) must be environment variables, not hardcoded.
- If any Langflow API call fails (auth error, connection refused), the UI should show a clear, human-readable error state — not a raw stack trace.

## UI Requirements

**Layout**
- Two-column layout: left column for live pipeline status, right column for the ask/answer panel.
- At the top of the page, show a horizontal pipeline stepper with 6 numbered stages (1. CSV, 2. Chunk, 3. Embed (Mistral), 4. Store (Chroma), 5. Retrieve, 6. Answer (Groq)), each as a badge with a short label, connected by arrows.

**Pipeline status panel (left) — LIVE, not static**
- A "Pipeline Status" card that calls `GET /pipeline-status` on page load.
- A live green/red **connection indicator** based on the `connected` field.
- The **actual live values** returned from the backend: collection name, total vectors stored, embedding dimensions, and last-checked timestamp.
- A manual **"Refresh Status"** button that re-calls `GET /pipeline-status` and updates the card without a full page reload.
- If `connected: false`, show a clear error state (e.g., "Cannot reach Langflow — check LANGFLOW_URL and API key") instead of blank/stale data.
- Below the live status card, show supplementary static context (source file name `ecom_test_cases.csv`, module list) — clearly labeled as reference info, separate from the live-fetched numbers.

**Ask panel (right)**
- Query textarea with an "Ask" button.
- Row of clickable suggested-question chips above the textarea (e.g., "Show me login test cases", "What negative test cases exist for payment?", "List edge cases for checkout") that populate the textarea on click.
- Answer section header shows the model name (from Groq, e.g. `llama-3.3-70b-versatile`) and token count if available from the Langflow response.
- Inline citation markers (e.g., 【Chunk 1】) embedded directly next to each claim in the answer text, referencing which retrieved test case chunk supports it.
- A "Top retrieved chunks" section below the answer showing each retrieved chunk's raw text (test case ID, module, title, etc.), matching the citation markers used in the answer.

**Styling**
- Dark theme with orange/amber accent color for buttons, badges, and highlights (instead of blue/purple).

## Response Parsing Logic (Langflow → Backend)

Langflow's `/api/v1/run/{flow_id}` response is a nested JSON structure. The final answer typically appears at:
response["outputs"][0]["outputs"][0]["results"]["message"]["text"]

However, retrieved chunks are **not** included by default — Langflow's `/run` endpoint only returns results for components explicitly wired to an output-type component (Chat Output, Text Output). To expose retrieved chunks:

### 1. Add a second output component in the Langflow flow
Wire Chroma DB's Search Results → Parser → a **second Chat/Text Output** component (e.g., named "Chunks Output"), separate from the main answer's Chat Output.

### 2. Use a delimiter-based template in the Parser component
Set the Parser's Template field to wrap each chunk with a machine-readable delimiter:

---CHUNK_START---
ID: {id}
Module: {module}
Text: {text}
---CHUNK_END---

Adjust `{id}`, `{module}`, `{text}` to match the actual field names present in Chroma DB's Search Results output (confirm via Run component → Inspect output on Chroma DB).

### 3. Backend parsing logic
```python
import re

def parse_langflow_response(data: dict) -> dict:
    all_outputs = data["outputs"][0]["outputs"]

    answer_text = None
    parser_text = None

    for output in all_outputs:
        component_name = output.get("component_display_name", "") or output.get("component_id", "")
        results = output.get("results", {})

        if "Chat Output" in component_name and "Chunks" not in component_name:
            answer_text = results.get("message", {}).get("text", "")

        if "Chunks Output" in component_name or "Parser" in component_name:
            parser_text = results.get("message", {}).get("text", "")

    chunks = []
    if parser_text:
        matches = re.findall(
            r"---CHUNK_START---\s*ID:\s*(.*?)\s*Module:\s*(.*?)\s*Text:\s*(.*?)\s*---CHUNK_END---",
            parser_text,
            re.DOTALL,
        )
        for chunk_id, module, text in matches:
            chunks.append({
                "id": chunk_id.strip(),
                "module": module.strip(),
                "text": text.strip(),
            })

    return {
        "answer": answer_text or "",
        "chunks": chunks,
    }
```

### 4. Map chunks to citation markers
Number the parsed chunks in retrieval order: Chunk 1, Chunk 2, Chunk 3, Chunk 4. The frontend displays these under "Top retrieved chunks" using this same numbering, so citation markers in the answer text (e.g., 【Chunk 2】) line up exactly with the corresponding chunk card shown below.

### 5. Error handling
- If `parser_text` is empty or the regex finds zero matches, don't fail the whole request — return the answer with an empty `chunks` array and let the frontend show a "No retrieval details available" note.
- If the Langflow response itself doesn't contain an `outputs` key (e.g., a 401/500 from Langflow), surface a clear error like `"Langflow request failed: <status/message>"` rather than a raw exception trace.