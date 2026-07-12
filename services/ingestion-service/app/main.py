"""
FastAPI ingestion service for the tunisian-legal-assistant RAG application.

Endpoints:
  POST /ingest            -> trigger PDF ingestion from PDF_DIR into Qdrant
  GET  /health            -> liveness probe
  GET  /collection/info   -> Qdrant collection statistics
"""
import logging

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from app.config import settings
from app.ingestion import run_ingestion
from app.logging_config import setup_logging
from app.models import CollectionInfoResponse, HealthResponse, IngestResponse
from app.qdrant_store import get_collection_info

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tunisian Legal Assistant - Ingestion Service",
    description="Ingests legal PDFs into a Qdrant vector store for RAG retrieval.",
    version="1.0.0",
)

# Tracks the state of the most recent background ingestion run.
_ingestion_state = {"running": False}


@app.get("/health", response_model=HealthResponse, tags=["monitoring"])
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/collection/info", response_model=CollectionInfoResponse, tags=["monitoring"])
def collection_info() -> CollectionInfoResponse:
    try:
        info = get_collection_info()
        return CollectionInfoResponse(**info)
    except LookupError as exc:
        logger.warning("Collection info requested but not found: %s", exc)
        raise HTTPException(status_code=404, detail=str(exc))
    except ConnectionError as exc:
        logger.error("Could not reach Qdrant: %s", exc)
        raise HTTPException(status_code=503, detail=f"Qdrant unavailable: {exc}")
    except Exception as exc:
        logger.exception("Unexpected error fetching collection info")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")


def _background_ingest() -> None:
    try:
        run_ingestion()
    except Exception:
        logger.exception("Background ingestion run failed")
    finally:
        _ingestion_state["running"] = False


@app.post("/ingest", response_model=IngestResponse, tags=["ingestion"])
def ingest(
    background_tasks: BackgroundTasks,
    background: bool = Query(
        default=False,
        description="If true, run ingestion asynchronously and return immediately.",
    ),
) -> IngestResponse:
    if _ingestion_state["running"]:
        raise HTTPException(
            status_code=409, detail="An ingestion run is already in progress."
        )

    if background:
        _ingestion_state["running"] = True
        background_tasks.add_task(_background_ingest)
        return IngestResponse(
            status="started",
            files_processed=0,
            chunks_ingested=0,
            files_failed=[],
            duration_seconds=0.0,
        )

    try:
        _ingestion_state["running"] = True
        result = run_ingestion()
        return IngestResponse(
            status="completed",
            files_processed=result.files_processed,
            chunks_ingested=result.chunks_ingested,
            files_failed=result.files_failed,
            duration_seconds=round(result.duration_seconds, 2),
        )
    except FileNotFoundError as exc:
        logger.error("PDF directory issue: %s", exc)
        raise HTTPException(status_code=404, detail=str(exc))
    except ConnectionError as exc:
        logger.error("Could not reach Qdrant during ingestion: %s", exc)
        raise HTTPException(status_code=503, detail=f"Qdrant unavailable: {exc}")
    except Exception as exc:
        logger.exception("Ingestion run failed")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")
    finally:
        _ingestion_state["running"] = False


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal error occurred."},
    )


@app.on_event("startup")
def on_startup() -> None:
    logger.info("Ingestion service starting up.")
    logger.info("PDF directory: %s", settings.pdf_dir)
    logger.info("Qdrant target: %s:%s", settings.qdrant_host, settings.qdrant_port)
    logger.info("Embedding model: %s", settings.embedding_model_name)
