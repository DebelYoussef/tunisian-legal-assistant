"""
POST /rag/query — the main RAG endpoint.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_rag_service
from app.models import RagQueryRequest, RagQueryResponse
from app.services.rag_service import RagOrchestrationError, RagService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/query", response_model=RagQueryResponse)
async def query(
    payload: RagQueryRequest,
    rag_service: RagService = Depends(get_rag_service),
) -> RagQueryResponse:
    logger.info(
        "RAG query received (session_id=%s, history_len=%d, question_len=%d)",
        payload.session_id,
        len(payload.conversation_history),
        len(payload.question),
    )
    try:
        response = rag_service.answer_question(
            question=payload.question,
            session_id=payload.session_id,
            conversation_history=payload.conversation_history,
        )
    except RagOrchestrationError as exc:
        logger.error("RAG orchestration error for session %s: %s", payload.session_id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to generate an answer: {exc}",
        ) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unhandled error processing RAG query for session %s", payload.session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing the query.",
        ) from exc

    logger.info(
        "RAG query completed (session_id=%s, sources=%d)",
        payload.session_id,
        len(response.sources),
    )
    return response
