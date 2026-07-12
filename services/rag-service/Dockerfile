FROM python:3.11-slim

WORKDIR /app

# System deps needed by sentence-transformers / torch at runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Pre-download the embedding model at build time to avoid cold-start
# downloads in production. Override EMBEDDING_MODEL_NAME to match runtime config.
ARG EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-large
ENV EMBEDDING_MODEL_NAME=${EMBEDDING_MODEL_NAME}

ENV PYTHONUNBUFFERED=1
EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=5s --start-period=300s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
