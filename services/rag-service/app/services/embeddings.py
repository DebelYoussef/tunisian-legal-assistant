"""
Embedding service around sentence-transformers.

Uses the E5 prefix convention:
  - "query: "   for retrieval queries
  - "passage: " for indexed documents (handled by the ingestion service)
"""
import logging
import threading

from sentence_transformers import SentenceTransformer

from app.config import get_settings

logger = logging.getLogger(__name__)

_QUERY_PREFIX = "query: "


class EmbeddingService:
    """Thread-safe singleton wrapper around a SentenceTransformer model."""

    _instance: "EmbeddingService | None" = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        settings = get_settings()
        logger.info(
            "Loading embedding model '%s' on device '%s'...",
            settings.embedding_model_name,
            settings.embedding_device,
        )
        try:
            self._model = SentenceTransformer(
                settings.embedding_model_name, device=settings.embedding_device
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load embedding model")
            raise RuntimeError(f"Could not load embedding model: {exc}") from exc

        self._dim = self._model.get_sentence_embedding_dimension()
        logger.info("Embedding model loaded (dim=%s)", self._dim)

    @classmethod
    def get_instance(cls) -> "EmbeddingService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_query(self, text: str) -> list[float]:
        """Embed a single user query using the E5 'query:' prefix convention."""
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")
        try:
            vector = self._model.encode(
                f"{_QUERY_PREFIX}{text.strip()}",
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            return vector.tolist()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Embedding failed for query")
            raise RuntimeError(f"Embedding failed: {exc}") from exc
