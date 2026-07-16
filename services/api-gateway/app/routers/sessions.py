"""
/api/sessions routes: chat session lifecycle management for authenticated users.
"""
import logging
from uuid import UUID
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db_pool
from app.dependencies import get_current_user
from app.models import SessionCreate, SessionOut, SessionUpdate, MessageOut, UserOut

logger = logging.getLogger("api-gateway.routers.sessions")
router = APIRouter(prefix="/api/sessions", tags=["sessions"])

# Helper function - NO DECORATOR
async def _get_owned_session(pool: asyncpg.Pool, session_id: UUID, user_id: UUID) -> None:
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

@router.get("", response_model=list[SessionOut], summary="List all sessions for current user")
async def get_sessions(
    current_user: UserOut = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_db_pool),
) -> list[SessionOut]:
    rows = await pool.fetch(
        "SELECT id, user_id, title, created_at FROM sessions WHERE user_id = $1 ORDER BY created_at DESC",
        current_user.id,
    )
    return [SessionOut(**row) for row in rows]

@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED, summary="Create new session")
async def create_session(
    payload: SessionCreate,
    current_user: UserOut = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_db_pool),
) -> SessionOut:
    row = await pool.fetchrow(
        "INSERT INTO sessions (user_id, title) VALUES ($1, $2) RETURNING id, user_id, title, created_at",
        current_user.id,
        payload.title,
    )
    return SessionOut(**row)

@router.get("/{session_id}/messages", response_model=list[MessageOut], summary="Get all messages for session")
async def get_session_messages(
    session_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_db_pool),
) -> list[MessageOut]:
    await _get_owned_session(pool, session_id, current_user.id)
    rows = await pool.fetch(
        "SELECT id, session_id, role, content, created_at FROM messages WHERE session_id = $1 ORDER BY created_at ASC",
        session_id,
    )
    return [MessageOut(**row) for row in rows]

@router.patch("/{session_id}", response_model=SessionOut, summary="Update session title")
async def update_session(
    session_id: UUID,
    payload: SessionUpdate,
    current_user: UserOut = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_db_pool),
) -> SessionOut:
    await _get_owned_session(pool, session_id, current_user.id)
    row = await pool.fetchrow(
        "UPDATE sessions SET title = $1 WHERE id = $2 RETURNING id, user_id, title, created_at",
        payload.title,
        session_id,
    )
    return SessionOut(**row)

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a session")
async def delete_session(
    session_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_db_pool),
):
    await _get_owned_session(pool, session_id, current_user.id)
    await pool.execute("DELETE FROM sessions WHERE id = $1", session_id)
