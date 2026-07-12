"""Generation via Openrouter."""

import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE = "https://openrouter.ai/api/v1"
GEN_MODEL = "deepseek/deepseek-chat"

GROUNDED_SYSTEM_PROMPT = """You are a VWO test case expert assistant. Use the retrieved test case chunks to answer the user's question.

Rules:
1. Answer based ONLY on the provided context.
2. Cite chunks as [Chunk N] where N is the chunk index (1-based).
3. If the context doesn't contain enough information, say so.
4. Keep answers clear, specific, and actionable.
5. Format with bullet points where appropriate."""

GENERATE_SYSTEM_PROMPT = """You are a VWO test case generator. Based on the retrieved test case templates and the user's request, generate a new structured test case.

Output format:
**Title:** <descriptive title>
**Preconditions:** <what needs to be set up>
**Steps:** <numbered steps>
**Expected:** <expected result>
**Priority:** <P0-P3>
**Tags:** <comma-separated tags>

Base the generated test case on similar test cases from the retrieved context.
If the user mentions a JIRA ID (e.g., VWO-1234), include it."""


def generate(
    query: str,
    chunks: list[dict],
    is_generate_mode: bool = False,
) -> tuple[str, str]:
    """Generate an answer using Openrouter. Returns (answer_text, model_name)."""
    if not OPENROUTER_API_KEY:
        return _fallback_answer(chunks, is_generate_mode), "no_api_key"

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        text = chunk.get("text", chunk.get("title", ""))
        jira = chunk.get("jira_id", "")
        module = chunk.get("module", "")
        context_parts.append(f"[Chunk {i}] (JIRA: {jira}, Module: {module})\n{text}")

    context = "\n\n".join(context_parts)

    system_prompt = GENERATE_SYSTEM_PROMPT if is_generate_mode else GROUNDED_SYSTEM_PROMPT

    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{OPENROUTER_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GEN_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1024,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            answer = data["choices"][0]["message"]["content"].strip()
            model_used = data.get("model", GEN_MODEL)
            return answer, model_used
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return _fallback_answer(chunks, is_generate_mode), f"error: {e}"


def _fallback_answer(chunks: list[dict], is_generate: bool) -> str:
    """Simple fallback when no API key is configured."""
    if is_generate:
        return "**Generate mode requires an Openrouter API key.**\n\nSet `OPENROUTER_API_KEY` in your `.env` file to enable AI-powered test case generation."
    if not chunks:
        return "No relevant test cases found. Try a different query or ingest test cases first."

    lines = ["**Fallback answer (no LLM):** Here are the most relevant test cases:\n"]
    for i, c in enumerate(chunks, 1):
        lines.append(f"**[Chunk {i}]** {c.get('title', 'Untitled')}")
        lines.append(f"   *Module:* {c.get('module', 'N/A')}  |  *Priority:* {c.get('priority', 'N/A')}")
        lines.append(f"   *JIRA:* {c.get('jira_id', 'N/A')}")
        lines.append("")

    return "\n".join(lines)
