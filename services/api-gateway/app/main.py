"""
API Gateway entrypoint for the tunisian-legal-assistant project.

Responsibilities:
- Own user authentication (register/login/me) backed by PostgreSQL + JWT
- Own chat session lifecycle (create/list/delete)
- Orchestrate RAG queries: persist history in PostgreSQL, delegate retrieval
  and generation to the downstream `rag-service`, persist the response
"""
import logging
import sys
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import db
from app.routers import auth, rag, sessions

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("api-gateway")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up %s", settings.service_name)
    await db.connect()
    yield
    logger.info("Shutting down %s", settings.service_name)
    await db.disconnect()


app = FastAPI(
    title="Tunisian Legal Assistant — API Gateway",
    description=(
        "Authentication, session management, and RAG query orchestration "
        "for the tunisian-legal-assistant platform."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: tighten allow_origins in production via a reverse proxy / env-driven
# allow-list. Left permissive here since Nginx sits in front in this stack.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------
# Global error handlers
# --------------------------------------------------------------------------
@app.exception_handler(asyncpg.PostgresError)
async def postgres_error_handler(request: Request, exc: asyncpg.PostgresError) -> JSONResponse:
    logger.exception("Unhandled PostgreSQL error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"},
    )


# --------------------------------------------------------------------------
# Routers
# --------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(rag.router)


# --------------------------------------------------------------------------
# Health check
# --------------------------------------------------------------------------
@app.get("/health", tags=["health"], summary="Service health check")
async def health() -> dict:
    pool_status = "connected" if db.pool is not None else "disconnected"
    return {
        "status": "ok",
        "service": settings.service_name,
        "database": pool_status,
    }
