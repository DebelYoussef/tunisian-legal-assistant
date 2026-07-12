"""
Thin HTTP client for the downstream `rag-service`.

Kept isolated from the router layer so the request/response contract with
the RAG service can evolve independently of the gateway's own API.
"""
import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger("api-gateway.rag_client")


class RAGServiceError(Exception):
    """Raised when the RAG service is unreachable or returns an error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


async def query_rag_service(
    question: str,
    history: list[dict[str, str]],
    session_id: str,
) -> dict[str, Any]:
    """
    Forward a question + conversation history to the RAG service and return
    its parsed JSON response.

    Expected downstream contract (POST {RAG_SERVICE_URL}/query):
        request:  {"question": str, "history": [{"role": ..., "content": ...}], "session_id": str}
        response: {"answer": str, "sources": [ ... ]}
    """
    settings = get_settings()
    url = f"{settings.rag_service_url.rstrip('/')}/query"
    payload = {
        "question": question,
        "history": history,
        "session_id": session_id,
    }

    try:
        async with httpx.AsyncClient(timeout=settings.rag_service_timeout) as client:
            response = await client.post(url, json=payload)
    except httpx.ConnectError as exc:
        logger.error("Could not connect to RAG service at %s: %s", url, exc)
        raise RAGServiceError("RAG service is unreachable") from exc
    except httpx.TimeoutException as exc:
        logger.error("RAG service timed out at %s: %s", url, exc)
        raise RAGServiceError("RAG service timed out") from exc
    except httpx.HTTPError as exc:
        logger.error("HTTP error calling RAG service: %s", exc)
        raise RAGServiceError(f"Error contacting RAG service: {exc}") from exc

    if response.status_code >= 400:
        logger.error(
            "RAG service returned error status %s: %s",
            response.status_code,
            response.text[:500],
        )
        raise RAGServiceError(
            f"RAG service returned status {response.status_code}",
            status_code=response.status_code,
        )

    try:
        data = response.json()
    except ValueError as exc:
        logger.error("RAG service returned non-JSON response: %s", exc)
        raise RAGServiceError("RAG service returned an invalid response") from exc

    if "answer" not in data:
        logger.error("RAG service response missing 'answer' field: %s", data)
        raise RAGServiceError("RAG service response missing 'answer' field")

    return data
