"""
Embedding generation and token-based chunking.

Uses the multilingual-e5-large model, which requires text to be prefixed
with "passage: " (for documents/chunks) or "query: " (for search queries)
per the E5 model card conventions. Chunk boundaries are computed using the
model's own tokenizer so chunk sizes are accurate token counts rather than
word/character approximations.
"""
import logging
import threading
from typing import Optional

from sentence_transformers import SentenceTransformer

from app.config import settings

logger = logging.getLogger(__name__)

_model: Optional[SentenceTransformer] = None
_model_lock = threading.Lock()


def get_model() -> SentenceTransformer:
    """Lazily load and cache the embedding model (thread-safe singleton)."""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                logger.info(
                    "Loading embedding model '%s' on device '%s'...",
                    settings.embedding_model_name,
                    settings.embedding_device,
                )
                _model = SentenceTransformer(
                    settings.embedding_model_name, device=settings.embedding_device
                )
                logger.info(
                    "Embedding model loaded. Vector dimension: %d",
                    _model.get_sentence_embedding_dimension(),
                )
    return _model


def get_embedding_dimension() -> int:
    return get_model().get_sentence_embedding_dimension()


def chunk_text(
    text: str,
    chunk_size_tokens: int = None,
    overlap_tokens: int = None,
) -> list[str]:
    """
    Split text into overlapping chunks measured in model tokens.
    Uses the underlying HuggingFace tokenizer of the sentence-transformers
    model so token counts match what the model will actually consume.
    """
    chunk_size_tokens = chunk_size_tokens or settings.chunk_size_tokens
    overlap_tokens = overlap_tokens or settings.chunk_overlap_tokens

    if overlap_tokens >= chunk_size_tokens:
        raise ValueError("overlap_tokens must be smaller than chunk_size_tokens")

    tokenizer = get_model().tokenizer
    # add_special_tokens=False keeps raw token counts aligned to plain text
    token_ids = tokenizer.encode(text, add_special_tokens=False)

    if not token_ids:
        return []

    chunks: list[str] = []
    step = chunk_size_tokens - overlap_tokens
    start = 0
    total = len(token_ids)

    while start < total:
        end = min(start + chunk_size_tokens, total)
        chunk_ids = token_ids[start:end]
        chunk_str = tokenizer.decode(chunk_ids, skip_special_tokens=True).strip()
        if chunk_str:
            chunks.append(chunk_str)
        if end == total:
            break
        start += step

    return chunks


def embed_passages(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for document chunks. E5 models require a "passage: "
    prefix for indexed documents (as opposed to "query: " used at search time).
    """
    if not texts:
        return []

    model = get_model()
    prefixed = [f"passage: {t}" for t in texts]
    embeddings = model.encode(
        prefixed,
        batch_size=settings.embedding_batch_size,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return embeddings.tolist()


def embed_query(text: str) -> list[float]:
    """Generate an embedding for a search query (uses the 'query: ' prefix)."""
    model = get_model()
    embedding = model.encode(
        f"query: {text}",
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return embedding.tolist()
