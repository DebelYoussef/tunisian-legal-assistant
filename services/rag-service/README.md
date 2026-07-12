# tunisian-legal-assistant — RAG Service

FastAPI microservice that answers legal questions over Tunisian law by
retrieving relevant chunks from Qdrant (`legal_docs` collection) and
generating an answer with Groq's `llama-3.1-8b-instant`.

## Endpoints

### `POST /rag/query`

**Request**
```json
{
  "question": "Quelles sont les conditions de validité d'un contrat ?",
  "session_id": "abc-123",
  "conversation_history": [
    {"role": "user", "content": "Bonjour"},
    {"role": "assistant", "content": "Bonjour, comment puis-je vous aider ?"}
  ]
}
```

**Response**
```json
{
  "answer": "En droit tunisien, la validité d'un contrat suppose...",
  "sources": [
    {
      "chunk_id": "b3f1...",
      "document_id": "coc_2023",
      "document_name": "Code des Obligations et des Contrats",
      "article_reference": "Article 2",
      "text": "Quatre conditions sont essentielles...",
      "score": 0.83,
      "metadata": {}
    }
  ],
  "session_id": "abc-123",
  "model": "llama-3.1-8b-instant"
}
```

### `GET /health`
Returns `{"status": "ok"}`.

## Configuration

All settings are environment variables (see `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `QDRANT_HOST` | `localhost` | Qdrant host |
| `QDRANT_PORT` | `6333` | Qdrant REST port |
| `GROQ_API_KEY` | — | Required. Groq API key |
| `EMBEDDING_MODEL_NAME` | `intfloat/multilingual-e5-large` | Sentence-transformers model, must match the ingestion service |
| `TOP_K` | `5` | Number of chunks retrieved per query |

## Running locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY=sk-...
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

## Running with Docker

```bash
docker build -t tla-rag-service .
docker run --rm -p 8002:8002 \
  -e QDRANT_HOST=host.docker.internal \
  -e GROQ_API_KEY=sk-... \
  tla-rag-service
```

## Notes / future extensions
- The E5 embedding model requires the `"query: "` prefix at retrieval time and
  `"passage: "` at indexing time (handled by the ingestion service) — this is
  already implemented in `app/services/embeddings.py`.
- `conversation_history` is trimmed to the last `MAX_HISTORY_MESSAGES` (default 10)
  to bound prompt size; adjust in `app/config.py` if needed.
- Retrieved context is capped by `MAX_CONTEXT_CHARS` to avoid blowing the Groq
  context window; tune per model.
- Consider adding response caching per `(session_id, question)` if repeated
  questions become common.
