"""
/api/sessions routes: chat session lifecycle management for authenticated
users. Deleting a session cascades to its messages via the FK constraint.
"""
import logging
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db_pool
from app.dependencies import get_current_user
from app.models import SessionCreate, SessionDeleteResponse, SessionOut, UserOut

logger = logging.getLogger("api-gateway.routers.sessions")

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post(
    "",
    response_model=SessionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat session",
)
async def create_session(
    payload: SessionCreate,
    current_user: UserOut = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_db_pool),
) -> SessionOut:
    title = payload.title.strip() if payload.title and payload.title.strip() else "New conversation"

    row = await pool.fetchrow(
        """
        INSERT INTO sessions (user_id, title)
        VALUES ($1, $2)
        RETURNING id, user_id, title, created_at
        """,
        current_user.id,
        title,
    )
    logger.info("Session created %s for user %s", row["id"], current_user.id)
    return SessionOut(**row)


@router.get(
    "",
    response_model=list[SessionOut],
    summary="List all sessions for the authenticated user",
)
async def list_sessions(
    current_user: UserOut = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_db_pool),
) -> list[SessionOut]:
    rows = await pool.fetch(
        """
        SELECT id, user_id, title, created_at
        FROM sessions
        WHERE user_id = $1
        ORDER BY created_at DESC
        """,
        current_user.id,
    )
    return [SessionOut(**row) for row in rows]


@router.delete(
    "/{session_id}",
    response_model=SessionDeleteResponse,
    summary="Delete a session and all of its messages",
)
async def delete_session(
    session_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_db_pool),
) -> SessionDeleteResponse:
    deleted_row = await pool.fetchrow(
        """
        DELETE FROM sessions
        WHERE id = $1 AND user_id = $2
        RETURNING id
        """,
        session_id,
        current_user.id,
    )

    if deleted_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    logger.info("Session deleted %s by user %s", session_id, current_user.id)
    return SessionDeleteResponse(id=session_id)
