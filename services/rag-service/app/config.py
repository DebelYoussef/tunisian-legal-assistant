"""
Centralized configuration for the RAG service.
All values are overridable via environment variables (or a .env file).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Service ---
    service_name: str = "tunisian-legal-assistant-rag"
    service_port: int = 8002
    log_level: str = "INFO"

    # --- Qdrant ---
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "legal_docs"
    qdrant_grpc_port: int = 6334
    qdrant_use_grpc: bool = False
    qdrant_search_timeout_s: float = 10.0

    # --- Embeddings ---
    embedding_model_name: str = "intfloat/multilingual-e5-large"
    embedding_device: str = "cpu"
    top_k: int = 5
    score_threshold: float | None = None  # e.g. 0.5 to filter weak matches

    # --- Groq / LLM ---
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    groq_temperature: float = 0.2
    groq_max_tokens: int = 1024
    groq_timeout_s: float = 30.0
    groq_max_retries: int = 2

    # --- Conversation ---
    max_history_messages: int = 10  # trailing messages kept from conversation_history
    max_context_chars: int = 6000  # cap on retrieved-context size injected into the prompt


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor so we parse env vars only once."""
    return Settings()
