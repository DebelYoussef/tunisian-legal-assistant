FROM python:3.11-slim

# System deps needed by PyMuPDF and torch/sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Directory the ingestion job reads PDFs from.
# In docker-compose, mount your host PDF folder to this path, e.g.:
#   volumes:
#     - ./data/pdfs:/app/data/pdfs:Z
RUN mkdir -p /app/data/pdfs

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
