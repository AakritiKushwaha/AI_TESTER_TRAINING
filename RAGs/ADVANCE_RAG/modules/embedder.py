"""Hybrid embedder using bge-m3 for dense + sparse vectors."""

import logging
import torch
import numpy as np
from transformers import AutoModel, AutoTokenizer

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None


def get_embedder():
    global _model, _tokenizer
    if _model is None:
        logger.info("Loading bge-m3 model (this may take a moment on first run)...")
        model_name = "BAAI/bge-m3"
        _model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
        _tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        if torch.cuda.is_available():
            _model = _model.to("cuda")
        _model.eval()
        logger.info("bge-m3 loaded.")
    return _model, _tokenizer


@torch.no_grad()
def embed(texts: list[str], batch_size: int = 16) -> tuple[list[list[float]], list[dict]]:
    """Return (dense_vectors, sparse_vectors) for a list of texts.

    sparse_vectors is a list of dicts mapping token_id (int) -> weight (float).
    """
    model, tokenizer = get_embedder()
    all_dense, all_sparse = [], []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        inputs = tokenizer(
            batch,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=8192,
        )
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}

        output = model(**inputs, return_dict=True)

        # Dense: mean pool over last hidden state
        attention_mask = inputs["attention_mask"]
        token_emb = output.last_hidden_state
        mask_expanded = attention_mask.unsqueeze(-1).float()
        sum_emb = (token_emb * mask_expanded).sum(dim=1)
        count = mask_expanded.sum(dim=1).clamp(min=1)
        dense = (sum_emb / count).cpu().numpy().tolist()
        all_dense.extend(dense)

        # Sparse: use the sparse_weights from bge-m3's forward (colbert linear output)
        # bge-m3 provides sparse_logits via the colbert module
        if hasattr(output, "sparse_logits"):
            sparse_logits = output.sparse_logits.cpu().numpy()
            sparse_weights = np.maximum(sparse_logits, 0)
            for row in sparse_weights:
                # Build {token_id: weight} dict for non-zero entries
                nonzero = np.where(row > 1e-6)[0]
                sparse_dict = {int(idx): float(row[idx]) for idx in nonzero}
                all_sparse.append(sparse_dict)
        else:
            # Fallback: compute simple lexical weights via attention mask
            input_ids = inputs["input_ids"].cpu().numpy()
            mask = inputs["attention_mask"].cpu().numpy()
            for j in range(len(batch)):
                ids = input_ids[j]
                m = mask[j]
                # Weight each present token equally
                unique_ids = set(ids[m == 1].tolist())
                weight = 1.0 / max(len(unique_ids), 1)
                all_sparse.append({int(tok): weight for tok in unique_ids})

    return all_dense, all_sparse


@torch.no_grad()
def embed_query(text: str) -> tuple[list[float], dict]:
    """Embed a single query. Returns (dense_vec, sparse_dict)."""
    dense, sparse_list = embed([text], batch_size=1)
    return dense[0], sparse_list[0]


def dense_dim() -> int:
    return 1024
