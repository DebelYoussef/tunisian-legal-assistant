"""
Qdrant search wrapper: turns a query vector into a list of scored chunks.
"""
import logging

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse
from qdrant_client.http.models import ScoredPoint

from app.config import Settings, get_settings
from app.models import SourceChunk

logger = logging.getLogger(__name__)


class QdrantSearchError(Exception):
    """Raised when the Qdrant collection is unreachable or misconfigured."""


class QdrantService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        try:
            self._client = QdrantClient(
                host=self._settings.qdrant_host,
                port=self._settings.qdrant_port,
                grpc_port=self._settings.qdrant_grpc_port,
                prefer_grpc=self._settings.qdrant_use_grpc,
                timeout=self._settings.qdrant_search_timeout_s,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to initialize Qdrant client")
            raise QdrantSearchError(f"Could not connect to Qdrant: {exc}") from exc

    def check_collection(self) -> bool:
        """Returns True if the configured collection exists and is reachable."""
        try:
            self._client.get_collection(self._settings.qdrant_collection)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("Qdrant collection check failed: %s", exc)
            return False

    def search(self, query_vector: list[float], top_k: int | None = None) -> list[SourceChunk]:
        k = top_k or self._settings.top_k
        try:
            results = self._client.search(
                collection_name=self._settings.qdrant_collection,
                query_vector=query_vector,
                limit=k,
                score_threshold=self._settings.score_threshold,
                with_payload=True,
            )
        except (UnexpectedResponse, ResponseHandlingException) as exc:
            logger.exception("Qdrant search failed")
            raise QdrantSearchError(f"Qdrant search failed: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected error during Qdrant search")
            raise QdrantSearchError(f"Unexpected Qdrant error: {exc}") from exc

        return [self._to_source_chunk(point) for point in results]

    @staticmethod
    def _to_source_chunk(point: ScoredPoint) -> SourceChunk:
        payload = point.payload or {}
        return SourceChunk(
            chunk_id=str(point.id),
            document_id=payload.get("document_id"),
            document_name=payload.get("document_name") or payload.get("source"),
            article_reference=payload.get("article_reference"),
            text=payload.get("text", ""),
            score=float(point.score),
            metadata={
                k: v
                for k, v in payload.items()
                if k not in {"text", "document_id", "document_name", "article_reference", "source"}
            },
        )
