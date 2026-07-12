"""
Core RAG orchestration: embed question -> search Qdrant -> build prompt -> call Groq.
"""
import logging

from app.config import Settings, get_settings
from app.models import ConversationMessage, RagQueryResponse, SourceChunk
from app.services.embeddings import EmbeddingService
from app.services.groq_service import GroqService, GroqServiceError
from app.services.qdrant_service import QdrantSearchError, QdrantService

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Tunisian legal expert assistant (assistant juridique tunisien).

Rules you must always follow:
1. Answer in the SAME language the user used to ask the question (French or Arabic). \
If the question mixes both, prefer the dominant language of the question.
2. Base your answer primarily on the legal excerpts provided in the "Contexte / السياق" \
section below. If the provided excerpts do not contain enough information to answer \
confidently, say so clearly instead of inventing an answer.
3. Whenever relevant, cite the specific law articles, codes, or texts you are relying on \
(e.g. "Article 24 du Code des Obligations et des Contrats" or "الفصل 24 من مجلة الالتزامات والعقود").
4. Always remind the user, at the end of your answer, that you are an AI assistant and that \
your response does not replace consultation with a licensed lawyer ("avocat") for their \
specific situation.
5. Be precise, structured, and neutral. Do not give definitive legal certainty where the law \
is ambiguous or fact-dependent.
"""


class RagOrchestrationError(Exception):
    """Wraps any downstream failure (embedding, search, or LLM) for the API layer."""


class RagService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._qdrant = QdrantService(self._settings)
        self._groq = GroqService(self._settings)

    def _embedder(self) -> EmbeddingService:
        # Lazily fetched each call so the singleton is created on first real use,
        # not necessarily at import time.
        return EmbeddingService.get_instance()

    def _build_context_block(self, chunks: list[SourceChunk]) -> str:
        parts = []
        total_len = 0
        for i, chunk in enumerate(chunks, start=1):
            ref = chunk.article_reference or chunk.document_name or f"source_{i}"
            snippet = f"[{i}] ({ref}) {chunk.text.strip()}"
            if total_len + len(snippet) > self._settings.max_context_chars:
                break
            parts.append(snippet)
            total_len += len(snippet)
        return "\n\n".join(parts) if parts else "(Aucun extrait pertinent trouvé.)"

    def _build_messages(
        self,
        question: str,
        history: list[ConversationMessage],
        context_block: str,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

        trimmed_history = history[-self._settings.max_history_messages :]
        for msg in trimmed_history:
            # system-role messages from client history are demoted to user context
            # to avoid overriding our own system prompt.
            role = msg.role.value if msg.role.value in ("user", "assistant") else "user"
            messages.append({"role": role, "content": msg.content})

        user_turn = (
            f"Contexte / السياق (extraits juridiques pertinents):\n{context_block}\n\n"
            f"Question: {question}"
        )
        messages.append({"role": "user", "content": user_turn})
        return messages

    def answer_question(
        self,
        question: str,
        session_id: str,
        conversation_history: list[ConversationMessage],
    ) -> RagQueryResponse:
        try:
            query_vector = self._embedder().embed_query(question)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Embedding step failed for session %s", session_id)
            raise RagOrchestrationError(f"Embedding failed: {exc}") from exc

        try:
            sources = self._qdrant.search(query_vector, top_k=self._settings.top_k)
        except QdrantSearchError as exc:
            logger.exception("Qdrant search failed for session %s", session_id)
            raise RagOrchestrationError(f"Vector search failed: {exc}") from exc

        context_block = self._build_context_block(sources)
        messages = self._build_messages(question, conversation_history, context_block)

        try:
            answer = self._groq.chat(messages)
        except GroqServiceError as exc:
            logger.exception("Groq completion failed for session %s", session_id)
            raise RagOrchestrationError(f"LLM generation failed: {exc}") from exc

        return RagQueryResponse(
            answer=answer,
            sources=sources,
            session_id=session_id,
            model=self._settings.groq_model,
        )
