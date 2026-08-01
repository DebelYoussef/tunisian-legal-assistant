"""
/api/auth routes: registration, login, and current-user lookup.
"""
import logging
from urllib.parse import urlencode

import asyncpg
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.database import get_db_pool
from app.dependencies import get_current_user
from app.models import TokenResponse, UserCreate, UserLogin, UserOut
from app.rate_limiter import check_rate_limit, record_failed_attempt, reset_attempts
from app.security import create_access_token, hash_password, verify_password

logger = logging.getLogger("api-gateway.routers.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


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
    email = payload.email.lower()

    await check_rate_limit(email)

    row = await pool.fetchrow(
        "SELECT id, password_hash FROM users WHERE email = $1",
        email,
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
        await record_failed_attempt(email)
        raise invalid_credentials

    if not verify_password(payload.password, row["password_hash"]):
        await record_failed_attempt(email)
        raise invalid_credentials

    await reset_attempts(email)
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


@router.get(
    "/google/login",
    summary="Redirect the user to Google's OAuth consent screen",
)
async def google_login() -> RedirectResponse:
    settings = get_settings()
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{urlencode(params)}")


@router.get(
    "/google/callback",
    summary="Handle Google's OAuth redirect and issue our own JWT",
)
async def google_callback(code: str, pool: asyncpg.Pool = Depends(get_db_pool)) -> RedirectResponse:
    settings = get_settings()

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != status.HTTP_200_OK:
            logger.error("Google token exchange failed: %s", token_resp.text)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not exchange authorization code with Google",
            )

        google_access_token = token_resp.json().get("access_token")
        if not google_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google did not return an access token",
            )

        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {google_access_token}"},
        )
        if userinfo_resp.status_code != status.HTTP_200_OK:
            logger.error("Google userinfo request failed: %s", userinfo_resp.text)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not fetch Google profile",
            )

        profile = userinfo_resp.json()

    google_id = profile.get("id")
    email = profile.get("email")

    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google profile is missing id or email",
        )

    email = email.lower()

    try:
        row = await pool.fetchrow(
            "SELECT id, google_id FROM users WHERE email = $1",
            email,
        )

        if row is None:
            row = await pool.fetchrow(
                """
                INSERT INTO users (email, password_hash, google_id)
                VALUES ($1, NULL, $2)
                RETURNING id
                """,
                email,
                google_id,
            )
            logger.info("New user registered via Google: %s", row["id"])
        elif row["google_id"] is None:
            await pool.execute(
                "UPDATE users SET google_id = $1 WHERE id = $2",
                google_id,
                row["id"],
            )
            logger.info("Linked Google account to existing user: %s", row["id"])
    except asyncpg.UniqueViolationError as exc:
        logger.info("Google login conflict for google_id: %s", google_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This Google account is already linked to a different user",
        ) from exc
    except asyncpg.PostgresError as exc:
        logger.exception("Database error during Google login")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not complete Google login due to a database error",
        ) from exc

    token = create_access_token(subject=str(row["id"]))
    redirect_url = f"http://localhost:80/auth/callback?{urlencode({'token': token})}"
    return RedirectResponse(redirect_url)
