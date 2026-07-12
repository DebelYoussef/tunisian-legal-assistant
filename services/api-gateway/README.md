# API Gateway — tunisian-legal-assistant

Auth, session management, and RAG query orchestration for the Tunisian legal
assistant platform. This is the single entry point the frontend/Nginx talks
to; it in turn calls `rag-service` for retrieval + generation.

## Endpoints

### Auth — `/api/auth`
| Method | Path              | Auth | Description                          |
|--------|-------------------|------|--------------------------------------|
| POST   | `/register`       | No   | Create a user (email + password)     |
| POST   | `/login`          | No   | Verify credentials, return JWT       |
| GET    | `/me`             | Yes  | Return current authenticated user    |

### Sessions — `/api/sessions`
| Method | Path              | Auth | Description                          |
|--------|-------------------|------|---------------------------------------|
| POST   | ``                | Yes  | Create a new chat session             |
| GET    | ``                | Yes  | List all sessions for the user        |
| DELETE | `/{session_id}`   | Yes  | Delete a session + its messages       |

### RAG — `/api/rag`
| Method | Path      | Auth | Description                                          |
|--------|-----------|------|-------------------------------------------------------|
| POST   | `/query`  | Yes  | Ask a question in a session; persists history, calls RAG service, persists + returns the answer |

### Misc
| Method | Path      | Auth | Description        |
|--------|-----------|------|---------------------|
| GET    | `/health` | No   | Health check        |

## Request/response examples

**Register**
```
POST /api/auth/register
{"email": "user@example.com", "password": "S3cur3Pass!"}
```

**Login**
```
POST /api/auth/login
{"email": "user@example.com", "password": "S3cur3Pass!"}
-> {"access_token": "...", "token_type": "bearer", "expires_in_minutes": 60}
```

**Create session**
```
POST /api/sessions
Authorization: Bearer <token>
{"title": "Contract law question"}
```

**RAG query**
```
POST /api/rag/query
Authorization: Bearer <token>
{"session_id": "<uuid>", "question": "What are the notice requirements for terminating a CDI contract?"}

-> {
  "session_id": "<uuid>",
  "answer": "...",
  "sources": [{"document": "...", "excerpt": "...", "score": 0.87}],
  "message_id": "<uuid>"
}
```

## Environment variables

See `.env.example`. Required:
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `JWT_SECRET`, `JWT_ALGORITHM` (default `HS256`), `JWT_EXPIRE_MINUTES` (default `60`)
- `RAG_SERVICE_URL` (default `http://rag-service:8002`)

## Database schema

Tables (`users`, `sessions`, `messages`) are created automatically on
startup via `CREATE TABLE IF NOT EXISTS`, including the `uuid-ossp`
extension for UUID generation. No separate migration step is required for
initial deployment.

```
users        (id uuid pk, email unique, password_hash, created_at)
sessions     (id uuid pk, user_id fk -> users.id, title, created_at)
messages     (id uuid pk, session_id fk -> sessions.id, role, content, created_at)
```

Deleting a session cascades to its messages (`ON DELETE CASCADE`).

## Running locally

```bash
pip install -r requirements.txt
cp .env.example .env   # edit as needed
uvicorn app.main:app --reload --port 8000
```

## Running via Docker

```bash
docker build -t api-gateway .
docker run --env-file .env -p 8000:8000 api-gateway
```

In the project's `docker-compose.yml`, this service should sit behind the
Nginx reverse proxy and depend on `postgres` and `rag-service` being
healthy before it fully starts serving RAG queries (the `/health` endpoint
reflects DB connectivity; the RAG service is only checked at query time).

## Notes / future extensions

- Rate limiting (e.g. per-user query throttling) is not yet implemented —
  recommended if exposed publicly.
- Refresh tokens are not implemented; only short-lived access tokens.
- `sources` in the RAG response is intentionally loosely typed
  (`list[dict]`) since it passes through whatever `rag-service` returns.
