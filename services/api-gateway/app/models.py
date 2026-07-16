"""
Pydantic schemas shared across routers: request bodies, response models,
and internal DTOs.
"""
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in_minutes: int


# --------------------------------------------------------------------------
# Sessions
# --------------------------------------------------------------------------
class SessionCreate(BaseModel):
    title: str | None = Field(default=None, max_length=255)

class SessionUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255) 
class SessionOut(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime


class SessionDeleteResponse(BaseModel):
    id: UUID
    deleted: bool = True


# --------------------------------------------------------------------------
# Messages
# --------------------------------------------------------------------------
class MessageOut(BaseModel):
    id: UUID
    session_id: UUID
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


# --------------------------------------------------------------------------
# RAG
# --------------------------------------------------------------------------
class RAGQueryRequest(BaseModel):
    session_id: UUID
    question: str = Field(min_length=1, max_length=4000)


class RAGSource(BaseModel):
    """Loosely typed to tolerate whatever shape the RAG service returns."""

    model_config = {"extra": "allow"}

    document: str | None = None
    excerpt: str | None = None
    score: float | None = None


class RAGQueryResponse(BaseModel):
    session_id: UUID
    answer: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    message_id: UUID
