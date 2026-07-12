"""Cross-encoder re-ranker using BAAI/bge-reranker-v2-m3."""

import logging
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None


def get_reranker():
    global _model, _tokenizer
    if _model is None:
        logger.info("Loading bge-reranker-v2-m3 (this may take a moment)...")
        model_name = "BAAI/bge-reranker-v2-m3"
        _model = AutoModelForSequenceClassification.from_pretrained(
            model_name, trust_remote_code=True
        )
        _tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        if torch.cuda.is_available():
            _model = _model.to("cuda")
        _model.eval()
        logger.info("bge-reranker-v2-m3 loaded.")
    return _model, _tokenizer


@torch.no_grad()
def rerank(
    query: str,
    documents: list[dict],
    top_k: int = 4,
) -> list[dict]:
    """Re-rank documents by cross-encoder relevance to the query.

    Each doc dict must have at least a 'text' key.
    Returns documents sorted by relevance (descending), limited to top_k.
    """
    if not documents:
        return []

    model, tokenizer = get_reranker()
    texts = [doc.get("text", doc.get("title", "")) for doc in documents]
    pairs = [[query, text] for text in texts]

    inputs = tokenizer(
        pairs,
        padding=True,
        truncation=True,
        return_tensors="pt",
        max_length=512,
    )
    if torch.cuda.is_available():
        inputs = {k: v.to("cuda") for k, v in inputs.items()}

    scores = model(**inputs).logits.squeeze(-1).cpu().numpy().tolist()
    if not isinstance(scores, list):
        scores = [scores]

    # Attach scores and sort
    scored = []
    for doc, score in zip(documents, scores):
        d = dict(doc)
        d["rerank_score"] = round(float(score), 4)
        scored.append(d)

    scored.sort(key=lambda x: -x["rerank_score"])
    return scored[:top_k]
