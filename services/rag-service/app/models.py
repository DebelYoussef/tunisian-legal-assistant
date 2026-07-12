"""
Pydantic schemas for the /rag/query endpoint and supporting structures.
"""
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Role(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ConversationMessage(BaseModel):
    role: Role
    content: str = Field(..., min_length=1, max_length=8000)


class RagQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field(..., min_length=1, max_length=128)
    conversation_history: list[ConversationMessage] = Field(default_factory=list)

    @field_validator("question")
    @classmethod
    def strip_question(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("question must not be empty or whitespace-only")
        return v


class SourceChunk(BaseModel):
    chunk_id: str
    document_id: str | None = None
    document_name: str | None = None
    article_reference: str | None = None
    text: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagQueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    session_id: str
    model: str


class HealthResponse(BaseModel):
    status: str = "ok"


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
