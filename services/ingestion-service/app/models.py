"""
Pydantic schemas for request/response bodies.
"""
from typing import Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class IngestResponse(BaseModel):
    status: str
    files_processed: int
    chunks_ingested: int
    files_failed: list[str] = []
    duration_seconds: float


class CollectionInfoResponse(BaseModel):
    collection_name: str
    status: str
    points_count: Optional[int] = None
    vectors_count: Optional[int] = None
    segments_count: Optional[int] = None
    vector_size: Optional[int] = None
    distance: Optional[str] = None


class ErrorResponse(BaseModel):
    detail: str
