"""
tunisian-legal-assistant — RAG service entrypoint.

Run locally:
    uvicorn app.main:app --host 0.0.0.0 --port 8002

Startup eagerly loads the embedding model and initializes the Qdrant/Groq
clients so the first real request isn't penalized with cold-start latency,
and so /health can reflect real readiness.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.logging_config import configure_logging
from app.models import ErrorResponse
from app.routers import health, rag
from app.services.embeddings import EmbeddingService
from app.services.rag_service import RagService

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s...", settings.service_name)
    try:
        # Warm the embedding model singleton once, at startup.
        EmbeddingService.get_instance()
        app.state.rag_service = RagService(settings)
        logger.info("RAG service initialized successfully.")
    except Exception:
        logger.exception("Fatal error during startup initialization")
        raise
    yield
    logger.info("Shutting down %s...", settings.service_name)


app = FastAPI(
    title="Tunisian Legal Assistant — RAG Service",
    description="Retrieval-augmented generation over Tunisian legal documents.",
    version="1.0.0",
    lifespan=lifespan,
)

# NOTE: tighten allow_origins in production (e.g. to the API gateway / frontend domain).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(error="internal_server_error", detail=str(exc)).model_dump(),
    )


app.include_router(health.router)
app.include_router(rag.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.service_port, reload=False)
