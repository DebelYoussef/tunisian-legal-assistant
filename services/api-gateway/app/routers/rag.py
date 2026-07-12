"""
/api/rag routes: the core orchestration endpoint that ties together
PostgreSQL-backed chat history and the downstream RAG service.
"""
import logging
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from app.config import get_settings
from app.database import get_db_pool
from app.dependencies import get_current_user
from app.models import RAGQueryRequest, RAGQueryResponse, UserOut
from app.services.rag_client import RAGServiceError, query_rag_service

logger = logging.getLogger("api-gateway.routers.rag")

router = APIRouter(prefix="/api/rag", tags=["rag"])


async def _get_owned_session(pool: asyncpg.Pool, session_id: UUID, user_id: UUID) -> None:
    """Raise 404 if the session doesn't exist or doesn't belong to the user."""
    row = await pool.fetchrow(
        "SELECT id FROM sessions WHERE id = $1 AND user_id = $2",
        session_id,
        user_id,
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )


@router.post(
    "/query",
    response_model=RAGQueryResponse,
    summary="Ask a question within a session, using RAG over legal documents",
)
async def rag_query(
    payload: RAGQueryRequest,
    current_user: UserOut = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_db_pool),
) -> RAGQueryResponse:
    settings = get_settings()

    await _get_owned_session(pool, payload.session_id, current_user.id)

    # (a) Save the user's message first, so it's persisted even if the
    # downstream RAG call subsequently fails.
    async with pool.acquire() as conn:
        user_msg_row = await conn.fetchrow(
            """
            INSERT INTO messages (session_id, role, content)
            VALUES ($1, 'user', $2)
            RETURNING id, created_at
            """,
            payload.session_id,
            payload.question,
        )
        logger.info(
            "Saved user message %s in session %s",
            user_msg_row["id"],
            payload.session_id,
        )

        # (b) Fetch last N messages (including the one we just inserted) in
        # chronological order to use as conversation history/context.
        history_rows = await conn.fetch(
            """
            SELECT role, content
            FROM (
                SELECT role, content, created_at
                FROM messages
                WHERE session_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            ) AS recent
            ORDER BY created_at ASC
            """,
            payload.session_id,
            settings.rag_history_limit,
        )

    history = [{"role": row["role"], "content": row["content"]} for row in history_rows]

    # (c) Forward question + history to the RAG service.
    try:
        rag_result = await query_rag_service(
            question=payload.question,
            history=history,
            session_id=str(payload.session_id),
        )
    except RAGServiceError as exc:
        logger.error("RAG service call failed for session %s: %s", payload.session_id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"RAG service error: {exc}",
        ) from exc

    answer = rag_result["answer"]
    sources = rag_result.get("sources", [])

    # (d) Save the assistant's response.
    assistant_msg_row = await pool.fetchrow(
        """
        INSERT INTO messages (session_id, role, content)
        VALUES ($1, 'assistant', $2)
        RETURNING id
        """,
        payload.session_id,
        answer,
    )
    logger.info(
        "Saved assistant message %s in session %s",
        assistant_msg_row["id"],
        payload.session_id,
    )

    # (e) Return answer + sources.
    return RAGQueryResponse(
        session_id=payload.session_id,
        answer=answer,
        sources=sources,
        message_id=assistant_msg_row["id"],
    )
