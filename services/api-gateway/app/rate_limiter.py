"""
Login brute-force protection backed by Redis.
"""
import logging

import redis.asyncio as redis
from fastapi import HTTPException, status

from app.config import get_settings

logger = logging.getLogger("api-gateway.rate_limiter")

MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 900  # 15 minutes

_settings = get_settings()

redis_client = redis.Redis(
    host=_settings.redis_host,
    port=_settings.redis_port,
    decode_responses=True,
)


def _key(email: str) -> str:
    return f"login_attempts:{email.lower()}"


async def check_rate_limit(email: str) -> None:
    """Raise 429 if the email has hit the failed-attempt limit."""
    key = _key(email)
    count = await redis_client.get(key)

    if count is not None and int(count) >= MAX_ATTEMPTS:
        ttl = await redis_client.ttl(key)
        retry_after = ttl if ttl and ttl > 0 else LOCKOUT_SECONDS
        logger.warning("Rate limit hit for email: %s", email)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives. Réessayez dans 15 minutes.",
            headers={"Retry-After": str(retry_after)},
        )


async def record_failed_attempt(email: str) -> None:
    """Increment the failed-attempt counter, setting a 15 min TTL on first attempt."""
    key = _key(email)
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, LOCKOUT_SECONDS)


async def reset_attempts(email: str) -> None:
    """Clear the failed-attempt counter after a successful login."""
    await redis_client.delete(_key(email))
