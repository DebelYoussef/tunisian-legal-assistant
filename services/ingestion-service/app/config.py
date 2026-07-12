"""
Centralized configuration for the ingestion service.
All values can be overridden via environment variables, which is how
they will typically be injected in the docker-compose.yml service definition.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # --- Qdrant ---
    qdrant_host: str = Field(default="localhost", env="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, env="QDRANT_PORT")
    qdrant_collection: str = Field(default="legal_docs", env="QDRANT_COLLECTION")
    qdrant_api_key: str | None = Field(default=None, env="QDRANT_API_KEY")

    # --- PDF ingestion ---
    pdf_dir: str = Field(default="/app/data/pdfs", env="PDF_DIR")

    # --- Chunking ---
    chunk_size_tokens: int = Field(default=500, env="CHUNK_SIZE_TOKENS")
    chunk_overlap_tokens: int = Field(default=50, env="CHUNK_OVERLAP_TOKENS")

    # --- Embedding model ---
    embedding_model_name: str = Field(
        default="intfloat/multilingual-e5-large", env="EMBEDDING_MODEL_NAME"
    )
    embedding_batch_size: int = Field(default=32, env="EMBEDDING_BATCH_SIZE")
    embedding_device: str = Field(default="cpu", env="EMBEDDING_DEVICE")  # "cpu" | "cuda"

    # --- Misc ---
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
