"""Query rewriting via Openrouter API."""

import os
import json
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE = "https://openrouter.ai/api/v1"
REWRITE_MODEL = "openai/gpt-4o-mini"  # Fast & cheap for rewrites

REWRITE_PROMPT = """You are a query expansion assistant for a test case search engine.

Given a user's question about VWO (Visual Website Optimizer) test cases,
generate 3 alternative phrasings that capture the same intent.
Return ONLY a JSON array of 3 strings, no other text.

Examples:
Input: "How do I create an A/B test campaign?"
Output: ["steps to set up an A/B test campaign","A/B campaign creation workflow","how to launch a split test experiment"]

Input: "{query}"
Output:"""


def rewrite_query(query: str) -> list[str]:
    """Generate alternative phrasings for the query using Openrouter."""
    if not OPENROUTER_API_KEY:
        logger.warning("No OPENROUTER_API_KEY set — skipping rewrite.")
        return [query]

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{OPENROUTER_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": REWRITE_MODEL,
                    "messages": [
                        {"role": "system", "content": REWRITE_PROMPT.format(query=query)},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 200,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip()

            # Try to parse JSON
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("\n", 1)[0]
            if content.startswith("```json"):
                content = content[7:].rsplit("```", 1)[0].strip()

            rewrites = json.loads(content)
            if isinstance(rewrites, list) and len(rewrites) >= 1:
                return rewrites[:3]
    except Exception as e:
        logger.warning(f"Query rewrite failed: {e}")

    return [query]
