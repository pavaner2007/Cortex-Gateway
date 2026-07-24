# Cortex Gateway

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-6366f1?style=for-the-badge)
![Phase](https://img.shields.io/badge/phase-1%20%E2%80%93%20Foundation-8b5cf6?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-06b6d4?style=for-the-badge)

**Enterprise AI Gateway Platform**

*Route, manage, and observe all your LLM traffic from a single control plane.*

</div>

---

## Overview

Cortex Gateway is a production-grade AI Infrastructure Platform that acts as an intelligent proxy between client applications and multiple Large Language Model providers (OpenAI, Gemini, Anthropic, Groq, Ollama, and more).

**Phase 1** establishes the production-ready foundation — clean architecture, observability, database/cache connectivity, and a beautiful monitoring dashboard. Future phases will add routing logic, provider integrations, auth, rate limiting, failover, and analytics.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Client Applications                   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────▼──────────────────────────────────┐
│                     Cortex Gateway                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Frontend  (React + TypeScript + Vite + TailwindCSS) │   │
│  └──────────────────────────┬───────────────────────────┘   │
│                             │ REST                          │
│  ┌──────────────────────────▼───────────────────────────┐   │
│  │  Backend   (FastAPI + Uvicorn + Async SQLAlchemy)    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │   │
│  │  │  Middleware  │  │  API Routes  │  │  Services  │  │   │
│  │  │  • CORS      │  │  • /health   │  │  • Redis   │  │   │
│  │  │  • Logging   │  │  • /version  │  │  • DB Sess │  │   │
│  │  │  • Timing    │  │  • /         │  │            │  │   │
│  │  │  • Errors    │  │              │  │            │  │   │
│  │  └──────────────┘  └──────────────┘  └────────────┘  │   │
│  └───────────────────────┬───────────────────┬──────────┘   │
│                          │                   │              │
│  ┌───────────────────────▼──┐  ┌─────────────▼──────────┐   │
│  │  PostgreSQL 16           │  │  Redis 7               │   │
│  │  (Async SQLAlchemy +     │  │  (Session cache,       │   │ 
│  │   Alembic migrations)    │  │   rate limiting)       │   │
│  └──────────────────────────┘  └────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
cortex-gateway/
├── backend/
│   ├── app/
│   │   ├── api/                  # Route handlers and API aggregator
│   │   │   └── endpoints/        # health, root, version endpoints
│   │   ├── core/                 # Config, exceptions, security primitives
│   │   ├── database/             # SQLAlchemy engine, session, Base, Alembic
│   │   │   └── migrations/       # Alembic env + version scripts
│   │   ├── logging/              # Loguru setup and logger factory
│   │   ├── middleware/           # CORS, logging, timing, error handler
│   │   ├── models/               # SQLAlchemy ORM models (future phases)
│   │   ├── providers/            # LLM provider adapters (future phases)
│   │   ├── schemas/              # Pydantic v2 request/response schemas
│   │   ├── services/             # Redis client and future service layer
│   │   ├── utils/                # Shared utilities (request ID, etc.)
│   │   └── main.py               # Application factory (create_app)
│   ├── tests/                    # Async pytest test suite
│   ├── Dockerfile
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                  # Axios client and endpoint wrappers
│   │   ├── components/           # Reusable UI components
│   │   ├── pages/                # Route-level page components
│   │   └── types/                # TypeScript interfaces
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docs/
│   └── architecture.md
├── infrastructure/               # Kubernetes manifests (future phases)
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## Prerequisites

| Tool | Version |
|------|---------|
| Docker | ≥ 24.x |
| Docker Compose | ≥ 2.x |
| Python | ≥ 3.12 (local dev) |
| Node.js | ≥ 20.x (local dev) |

---

## Quick Start (Docker)

```bash
# 1. Clone the repository
git clone https://github.com/your-org/cortex-gateway.git
cd cortex-gateway

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env with your values (especially SECRET_KEY in production)

# 3. Build and start all services
docker compose up --build

# 4. Verify services are running
curl http://localhost:8000/health
```

Services will be available at:

| Service | URL |
|---------|-----|
| Frontend Dashboard | http://localhost |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

---

## Local Development Setup

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.\.venv\Scripts\Activate.ps1     # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example ../.env

# Start PostgreSQL and Redis via Docker (infrastructure only)
docker compose up postgres redis -d

# Run Alembic migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the Vite dev server (proxies /api to http://localhost:8000)
npm run dev
```

Frontend will be available at http://localhost:5173 in development mode.

---

## Database Migrations (Alembic)

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "describe your change"

# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# View migration history
alembic history --verbose
```

---

## Running Tests

```bash
cd backend
pytest tests/ -v --asyncio-mode=auto
```

---

## API Endpoints (Phase 1)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Project information |
| GET | `/health` | System health check (DB + Redis) |
| GET | `/version` | Version metadata |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc documentation |

---

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application display name | `Cortex Gateway` |
| `APP_VERSION` | Current version | `1.0.0` |
| `ENVIRONMENT` | `development` / `staging` / `production` | `development` |
| `DEBUG` | Enable debug mode | `false` |
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_DB` | Database name | `cortex_gateway` |
| `POSTGRES_USER` | Database user | `cortex` |
| `POSTGRES_PASSWORD` | Database password | — |
| `DATABASE_URL` | Full async DB URL (auto-computed) | — |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_URL` | Full Redis URL (auto-computed) | — |
| `SECRET_KEY` | JWT/session signing key | — |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

---

## Development Workflow

1. **Feature branches**: `feature/<name>` off `main`
2. **Conventional commits**: `feat:`, `fix:`, `chore:`, `docs:`
3. **Tests**: All new endpoints must have corresponding pytest tests
4. **Migrations**: Never edit existing migration files — always create new ones
5. **Schemas**: All request/response models must use Pydantic v2
6. **Logging**: Use `get_logger(__name__)` — never use `print()`

---

## Phases Roadmap

| Phase | Focus |
|-------|-------|
| **1 – Foundation** ✅ | Project scaffold, DB/Redis, health endpoints, dashboard |
| 2 – Auth | API key management, JWT, tenant isolation |
| 3 – Providers | OpenAI, Gemini, Anthropic, Groq, Ollama adapters |
| 4 – Routing | Intelligent provider selection, fallback chains |
| 5 – Reliability | Circuit breakers, retries, rate limiting |
| 6 – Observability | Metrics, distributed tracing, cost analytics |
| 7 – Kubernetes | Helm charts, HPA, production deployment |

---

## License

[MIT](LICENSE) © 2024 Cortex Gateway Contributors
