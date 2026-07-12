"""
FastAPI dependency providers. The RagService instance is created once at
startup and stored on app.state, so requests reuse the same Qdrant/Groq
clients and the embedding model stays loaded in memory.
"""
from fastapi import Request

from app.services.rag_service import RagService


def get_rag_service(request: Request) -> RagService:
    service: RagService | None = getattr(request.app.state, "rag_service", None)
    if service is None:
        raise RuntimeError("RagService is not initialized on app.state")
    return service
