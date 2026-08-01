# Assistant Juridique Tunisien 🧑‍⚖️

A production-ready **RAG (Retrieval-Augmented Generation)** microservices platform that answers questions about Tunisian law, grounded in real legal texts (Code Civil, Code de Commerce, Code du Travail) with cited sources.

Built as a portfolio project demonstrating microservices architecture, authentication, observability, and CI/CD practices for a DevOps/Cloud engineering role.

---




## 📐 Architecture

```
                              Internet
                                 │
                              Nginx (reverse proxy, port 80)
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
           Frontend         API Gateway      Ingestion Service
          (Next.js 14)    (FastAPI, JWT,      (PDF → chunks →
                          Google OAuth)         embeddings)
                                 │                │
                                 │                │
                            RAG Service ──────────┘
                          (retrieval + Groq LLM)
                                 │
                ┌────────────────┼────────────────┬──────────────┐
                │                │                │              │
           PostgreSQL         Qdrant            Redis        Groq API
       (users, sessions,    (vector store    (rate limiting)  (LLM inference)
          messages)         for legal docs)

                        Monitoring stack
              Prometheus ──── Grafana ──── cAdvisor
           (metrics scraping) (dashboards)  (container metrics)
```

### Services

| Service | Tech | Responsibility |
|---|---|---|
| **nginx** | Nginx | Reverse proxy — routes `/` to frontend, `/api/*` to API Gateway |
| **frontend** | Next.js 14, TypeScript, Tailwind | Chat UI, auth pages, session management |
| **api-gateway** | FastAPI, asyncpg | Auth (JWT + Google OAuth), session/message persistence, RAG orchestration, rate limiting |
| **rag-service** | FastAPI, sentence-transformers, Groq SDK | Embeds queries, retrieves relevant legal chunks from Qdrant, generates answers via Groq |
| **ingestion-service** | FastAPI, PyMuPDF | Parses legal PDFs, chunks text, generates embeddings, stores in Qdrant |
| **postgres** | PostgreSQL 16 | Users, sessions, chat messages |
| **qdrant** | Qdrant | Vector store for legal document embeddings |
| **redis** | Redis 7 | Login attempt tracking for brute-force protection |
| **prometheus** | Prometheus | Scrapes `/metrics` from all FastAPI services + cAdvisor |
| **grafana** | Grafana | Dashboards: request rate, latency, container CPU/memory |
| **cadvisor** | cAdvisor | Per-container resource metrics (CPU, memory, network) |

---

## ✨ Features

### Core RAG functionality
- Semantic search over Tunisian legal codes (Code Civil, Code de Commerce, Code du Travail)
- Multilingual embeddings (French / Arabic) via `sentence-transformers`
- Source citations returned alongside every answer
- Conversation history maintained per session, included in LLM context

### Authentication & security
- Email/password registration with bcrypt hashing
- **Google OAuth 2.0** login/registration
- **Email verification** via Resend (transactional email)
- **Rate limiting**: 5 failed login attempts → 15-minute lockout (Redis-backed, per-email)
- JWT-based session auth

### Frontend
- Multi-conversation chat interface with rename/delete
- Auto-generated conversation titles from first message
- Dark / light theme toggle
- Collapsible legal source citations per response
- Mobile-responsive layout

### DevOps & observability
- Fully containerized with Docker Compose (11 services)
- CI pipeline on GitHub Actions: build, boot, health-check all services on every push
- Prometheus + Grafana + cAdvisor monitoring stack
  - Request rate and latency per service
  - CPU / memory usage per container
- Nginx as reverse proxy and single entry point

---

## 🛠️ Tech Stack

**Backend:** FastAPI · Python 3.11/3.12 · asyncpg · Pydantic
**Frontend:** Next.js 14 · TypeScript · Tailwind CSS · shadcn/ui
**AI/RAG:** Qdrant · sentence-transformers · Groq API (Llama 3.1)
**Data:** PostgreSQL 16 · Redis 7
**Infra:** Docker · Docker Compose · Nginx
**Observability:** Prometheus · Grafana · cAdvisor
**CI/CD:** GitHub Actions
**Auth:** JWT · Google OAuth 2.0 · bcrypt · Resend (email)

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- A [Groq API key](https://console.groq.com) (free tier available)
- A [Google Cloud OAuth client](https://console.cloud.google.com) (for Google login)
- A [Resend API key](https://resend.com) (for email verification)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/DebelYoussef/tunisian-legal-assistant.git
   cd tunisian-legal-assistant
   ```

2. **Configure environment variables**

   Create a `.env` file in the project root:
   ```bash
   # PostgreSQL
   POSTGRES_USER=legaluser
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=legaldb

   # JWT
   JWT_SECRET=your_random_secret_min_32_chars
   JWT_ALGORITHM=HS256
   JWT_EXPIRE_MINUTES=60

   # Groq
   GROQ_API_KEY=your_groq_api_key

   # Google OAuth
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GOOGLE_REDIRECT_URI=http://localhost:80/api/auth/google/callback

   # Email verification
   RESEND_API_KEY=your_resend_api_key

   # Frontend
   NEXT_PUBLIC_API_BASE_URL=http://localhost:80
   ```

3. **Add legal source PDFs**

   Place your legal text PDFs (Code Civil, Code de Commerce, Code du Travail, etc.) in:
   ```bash
   data/pdfs/
   ```

4. **Build and start all services**
   ```bash
   docker compose up -d --build
   ```

5. **Ingest the legal documents into Qdrant**
   ```bash
   curl -X POST http://localhost:8001/ingest
   ```

6. **Access the application**

   | Service | URL |
   |---|---|
   | App | http://localhost:80 |
   | Grafana | http://localhost:3001 (admin / admin on first login) |
   | Prometheus | http://localhost:9090 |
   | cAdvisor | http://localhost:8888 |
   | Qdrant dashboard | http://localhost:6333/dashboard |

---

## 📁 Project Structure

```
tunisian-legal-assistant/
├── services/
│   ├── ingestion-service/      # PDF → chunks → embeddings → Qdrant
│   ├── rag-service/            # Retrieval + generation
│   └── api-gateway/            # Auth, sessions, RAG orchestration
│       └── app/
│           ├── routers/        # auth.py, sessions.py, rag.py
│           ├── rate_limiter.py # Redis brute-force protection
│           ├── email_service.py# Resend transactional email
│           ├── database.py     # asyncpg pool + schema
│           └── config.py       # Settings (env vars)
├── frontend/                   # Next.js 14 app
│   ├── app/
│   │   ├── login/ register/    # Auth pages
│   │   ├── auth/callback/      # OAuth token handoff
│   │   ├── verify-email/       # Email verification landing
│   │   └── chat/[sessionId]/   # Main chat interface
│   └── components/             # Sidebar, ChatMessage, SourcesPanel...
├── infrastructure/
│   ├── nginx/nginx.conf
│   └── prometheus/prometheus.yml
├── data/pdfs/                   # Legal source documents
├── .github/workflows/ci.yml    # CI pipeline
└── docker-compose.yml
```

---

## 🔐 Security Notes

- Passwords hashed with bcrypt (never stored in plaintext)
- JWT tokens signed with HS256, configurable expiry
- Login rate limiting via Redis (5 attempts / 15 min lockout, keyed by email)
- Login timing normalized (dummy bcrypt check on unknown emails) to prevent user enumeration
- Google OAuth users are pre-verified (no password stored, `password_hash` nullable)
- CORS configured for the reverse-proxy setup (tighten `allow_origins` for production)

---

## 📊 Monitoring

Every FastAPI service exposes a `/metrics` endpoint (via `prometheus-fastapi-instrumentator`), scraped by Prometheus every 15 seconds. Grafana dashboards include:

- Request rate per service (`sum(rate(http_requests_total[5m])) by (job)`)
- Average response latency per endpoint
- Per-container CPU usage (via cAdvisor)
- Per-container memory usage (via cAdvisor)

---

## 🧪 CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push/PR to `main`:

1. Builds all Docker images
2. Boots the full stack
3. Health-checks `ingestion-service` and `api-gateway`
4. Tears down cleanly

---

## 🗺️ Roadmap

- [ ] AWS EC2 deployment with GitHub Actions CD pipeline
- [ ] Domain + HTTPS via Let's Encrypt
- [ ] Verified sending domain for unrestricted email delivery
- [ ] Kubernetes migration path (architecture already supports horizontal scaling)

---

## 📄 License

This project is a personal portfolio project. Feel free to explore the code for learning purposes.

---

## 👤 Author

**Youssef Debel**
Engineering student (ING-3) specializing in networking, systems, and cloud — building toward a DevOps/Cloud engineering career.

[GitHub](https://github.com/DebelYoussef) · [LinkedIn](#)