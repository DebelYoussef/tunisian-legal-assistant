# Ingestion Service — tunisian-legal-assistant

FastAPI microservice that ingests legal PDFs into Qdrant for the RAG pipeline.

## What it does

1. `POST /ingest` reads every `.pdf` in `PDF_DIR` (default `/app/data/pdfs/`) using **PyMuPDF**.
2. Splits each page's text into **500-token chunks with 50-token overlap**, using the
   embedding model's own tokenizer for accurate counts.
3. Embeds chunks with **`intfloat/multilingual-e5-large`** (French + Arabic support,
   1024-dim vectors, cosine distance). Chunks are prefixed with `"passage: "` per the
   E5 model's convention — use `"query: "` when embedding search queries elsewhere in
   your retrieval service.
4. Upserts vectors + payload (`filename`, `page_number`, `chunk_index`, `text`) into
   the Qdrant collection `legal_docs` (auto-created on first run).

## Endpoints

| Method | Path               | Description                                   |
|--------|--------------------|------------------------------------------------|
| POST   | `/ingest`          | Run ingestion. `?background=true` to run async |
| GET    | `/health`          | Liveness probe → `{"status": "ok"}`            |
| GET    | `/collection/info` | Qdrant collection stats                        |

## Environment variables

See `.env.example`. Key ones:

- `QDRANT_HOST` (default `localhost`)
- `QDRANT_PORT` (default `6333`)
- `PDF_DIR` (default `/app/data/pdfs`)

## docker-compose integration

```yaml
services:
  ingestion-service:
    build: ./ingestion-service
    container_name: ingestion-service
    environment:
      QDRANT_HOST: qdrant
      QDRANT_PORT: 6333
      PDF_DIR: /app/data/pdfs
    volumes:
      # :Z relabels the bind mount for SELinux (Fedora) so the container can read it
      - ./data/pdfs:/app/data/pdfs:Z
    depends_on:
      - qdrant
    networks:
      - backend
```

On Fedora/SELinux, if you hit a `Permission denied` reading PDFs from the mounted
volume, confirm the bind mount uses `:Z` (as above) or run:

```bash
sudo semanage fcontext -a -t container_file_t "/path/to/data/pdfs(/.*)?"
sudo restorecon -Rv /path/to/data/pdfs
```

## Local run (without Docker)

```bash
pip install -r requirements.txt
export QDRANT_HOST=localhost QDRANT_PORT=6333 PDF_DIR=./data/pdfs
uvicorn app.main:app --reload
```

## Notes on production readiness

- Embedding model is loaded lazily and cached as a singleton (loaded once per process).
- `/ingest` rejects concurrent runs with `409 Conflict` to avoid duplicate/racing writes.
- `/ingest?background=true` returns immediately and runs ingestion in a background task
  — poll `/collection/info` to watch `points_count` grow.
- Per-file failures (corrupt PDFs, etc.) are caught and reported in `files_failed`
  rather than aborting the whole batch.
- Re-running `/ingest` re-embeds and re-inserts all PDFs (points get new UUIDs), so if
  you need idempotent re-ingestion, clear the collection first or extend the payload
  with a content hash to dedupe on.
