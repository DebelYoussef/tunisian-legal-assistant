"""
Qdrant client wrapper: connection handling, collection lifecycle, and upserts.
"""
import logging
import uuid
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.exceptions import UnexpectedResponse

from app.config import settings

logger = logging.getLogger(__name__)

_client: Optional[QdrantClient] = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        logger.info(
            "Connecting to Qdrant at %s:%s", settings.qdrant_host, settings.qdrant_port
        )
        _client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key,
        )
    return _client


def ensure_collection(vector_size: int) -> None:
    """Create the collection if it doesn't already exist."""
    client = get_client()
    collection_name = settings.qdrant_collection

    try:
        existing = {c.name for c in client.get_collections().collections}
    except Exception as exc:
        logger.error("Failed to reach Qdrant while listing collections: %s", exc)
        raise ConnectionError(f"Could not connect to Qdrant: {exc}") from exc

    if collection_name in existing:
        logger.info("Collection '%s' already exists.", collection_name)
        return

    logger.info(
        "Creating collection '%s' with vector size %d", collection_name, vector_size
    )
    client.create_collection(
        collection_name=collection_name,
        vectors_config=qmodels.VectorParams(
            size=vector_size, distance=qmodels.Distance.COSINE
        ),
    )


def upsert_chunks(
    texts: list[str],
    embeddings: list[list[float]],
    filenames: list[str],
    page_numbers: list[int],
    chunk_indices: list[int],
) -> int:
    """
    Upsert a batch of chunks + embeddings + metadata into the collection.
    Returns the number of points upserted.
    """
    if not (len(texts) == len(embeddings) == len(filenames) == len(page_numbers) == len(chunk_indices)):
        raise ValueError("All input lists to upsert_chunks must have equal length")

    if not texts:
        return 0

    client = get_client()
    points = [
        qmodels.PointStruct(
            id=str(uuid.uuid4()),
            vector=embeddings[i],
            payload={
                "text": texts[i],
                "filename": filenames[i],
                "page_number": page_numbers[i],
                "chunk_index": chunk_indices[i],
            },
        )
        for i in range(len(texts))
    ]

    try:
        client.upsert(collection_name=settings.qdrant_collection, points=points)
    except UnexpectedResponse as exc:
        logger.error("Qdrant rejected the upsert batch: %s", exc)
        raise
    except Exception as exc:
        logger.error("Unexpected error while upserting to Qdrant: %s", exc)
        raise

    return len(points)


def get_collection_info() -> dict:
    client = get_client()
    collection_name = settings.qdrant_collection

    try:
        info = client.get_collection(collection_name=collection_name)
    except (UnexpectedResponse, ValueError) as exc:
        raise LookupError(f"Collection '{collection_name}' not found: {exc}") from exc

    vectors_config = info.config.params.vectors
    # vectors_config can be a single VectorParams or a dict of named vectors
    if isinstance(vectors_config, qmodels.VectorParams):
        vector_size = vectors_config.size
        distance = str(vectors_config.distance)
    else:
        vector_size = None
        distance = None

    return {
        "collection_name": collection_name,
        "status": str(info.status),
        "points_count": info.points_count,
        "vectors_count": info.vectors_count,
        "segments_count": info.segments_count,
        "vector_size": vector_size,
        "distance": distance,
    }
