"""
/api/auth routes: registration, login, and current-user lookup.
"""
import logging

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from app.config import get_settings
from app.database import get_db_pool
from app.dependencies import get_current_user
from app.models import TokenResponse, UserCreate, UserLogin, UserOut
from app.security import create_access_token, hash_password, verify_password

logger = logging.getLogger("api-gateway.routers.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account",
)
async def register(payload: UserCreate, pool: asyncpg.Pool = Depends(get_db_pool)) -> UserOut:
    password_hash = hash_password(payload.password)

    try:
        row = await pool.fetchrow(
            """
            INSERT INTO users (email, password_hash)
            VALUES ($1, $2)
            RETURNING id, email, created_at
            """,
            payload.email.lower(),
            password_hash,
        )
    except asyncpg.UniqueViolationError as exc:
        logger.info("Registration attempted with existing email: %s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from exc
    except asyncpg.PostgresError as exc:
        logger.exception("Database error during registration")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user due to a database error",
        ) from exc

    logger.info("New user registered: %s", row["id"])
    return UserOut(id=row["id"], email=row["email"], created_at=row["created_at"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT access token",
)
async def login(payload: UserLogin, pool: asyncpg.Pool = Depends(get_db_pool)) -> TokenResponse:
    row = await pool.fetchrow(
        "SELECT id, password_hash FROM users WHERE email = $1",
        payload.email.lower(),
    )

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if row is None:
        # Avoid leaking whether the email exists via timing differences by
        # still running a (dummy) bcrypt verification.
        verify_password(payload.password, "$2b$12$" + "0" * 53)
        raise invalid_credentials

    if not verify_password(payload.password, row["password_hash"]):
        raise invalid_credentials

    settings = get_settings()
    token = create_access_token(subject=str(row["id"]))
    logger.info("User logged in: %s", row["id"])

    return TokenResponse(access_token=token, expires_in_minutes=settings.jwt_expire_minutes)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Return the authenticated user's profile",
)
async def get_me(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    return current_user
