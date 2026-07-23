# Cortex Gateway – Architecture Documentation

## Overview

Cortex Gateway is built on **Clean Architecture** principles, separating concerns into concentric layers where inner layers have zero knowledge of outer layers.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Interface Layer (FastAPI routes, Pydantic schemas, HTTP middleware)        │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Application Layer (Use cases / service orchestration – future phases)     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Domain Layer (Business entities, domain events – future phases)           │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Infrastructure Layer (SQLAlchemy, Redis, HTTP clients)                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Diagram

```
                         ┌────────────────────────────┐
                         │      React Frontend         │
                         │  Vite + TypeScript          │
                         │  TailwindCSS                │
                         │  React Query (polling)      │
                         └────────────┬───────────────┘
                                      │ HTTP /api/*
                         ┌────────────▼───────────────┐
                         │     Nginx (production)      │
                         │   Static serving + proxy    │
                         └────────────┬───────────────┘
                                      │ proxy_pass
          ┌───────────────────────────▼──────────────────────────┐
          │                    FastAPI Application                │
          │                                                       │
          │  ┌─────────────────────────────────────────────────┐ │
          │  │               Middleware Stack                   │ │
          │  │  CORSMiddleware → TimingMiddleware →             │ │
          │  │  LoggingMiddleware → ErrorHandlerMiddleware      │ │
          │  └───────────────────────┬─────────────────────────┘ │
          │                          │                           │
          │  ┌───────────────────────▼─────────────────────────┐ │
          │  │               APIRouter                          │ │
          │  │  GET /         GET /health      GET /version     │ │
          │  └───────────────────────┬─────────────────────────┘ │
          │                          │                           │
          │  ┌───────────────────────▼─────────────────────────┐ │
          │  │           Dependency Injection                   │ │
          │  │  get_db() → AsyncSession                        │ │
          │  │  get_redis() → Redis                            │ │
          │  └─────────────────────────────────────────────────┘ │
          └──────────────────┬────────────────┬─────────────────┘
                             │                │
              ┌──────────────▼───┐    ┌───────▼──────────┐
              │  PostgreSQL 16   │    │    Redis 7         │
              │  asyncpg driver  │    │  redis.asyncio    │
              │  Alembic migs    │    │  health_check_    │
              └──────────────────┘    │  interval=30s     │
                                      └───────────────────┘
```

---

## Request Lifecycle

```
Client Request
     │
     ▼
CORSMiddleware          ← Handles OPTION preflight, injects CORS headers
     │
     ▼
TimingMiddleware        ← Records start timestamp
     │
     ▼
LoggingMiddleware       ← Assigns X-Request-ID, logs "Request received"
     │
     ▼
ErrorHandlerMiddleware  ← try/except safety net
     │
     ▼
FastAPI Exception Handlers (CortexException, ValidationError, etc.)
     │
     ▼
Route Handler           ← Business logic; injects DB/Redis via Depends()
     │
     ▼
[Response bubbles back up through the same middleware stack]
     │
     ▼
LoggingMiddleware       ← Logs "Response sent" with status + duration
     │
     ▼
TimingMiddleware        ← Appends X-Process-Time header
     │
     ▼
Client Response
```

---

## Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `app/main.py` | Application factory; registers middleware, routers, lifecycle hooks |
| `app/core/config.py` | Typed settings loaded from env vars via pydantic-settings |
| `app/core/exceptions.py` | Exception hierarchy + global FastAPI exception handlers |
| `app/database/session.py` | Async engine + session factory + `get_db()` dependency |
| `app/database/base.py` | Declarative Base with constraint naming conventions |
| `app/database/migrations/` | Alembic async migration environment |
| `app/services/redis_client.py` | Async Redis client + `get_redis()` dependency |
| `app/middleware/logging.py` | Request ID injection, structured request/response logging |
| `app/middleware/timing.py` | `X-Process-Time` response header |
| `app/middleware/error_handler.py` | Catch-all exception → JSON 500 |
| `app/logging/logger.py` | Loguru setup (stdout + rotating JSON file) |
| `app/schemas/common.py` | Pydantic v2 response models shared across endpoints |
| `app/api/router.py` | Aggregates all sub-routers; included once in `main.py` |
| `app/api/endpoints/health.py` | `GET /health` – live DB + Redis connectivity |
| `app/api/endpoints/root.py` | `GET /` – project info |
| `app/api/endpoints/version.py` | `GET /version` – runtime metadata |

---

## Technology Decisions

### Why AsyncPG over Psycopg2?
AsyncPG is a pure-async PostgreSQL driver with significantly better throughput under concurrent load — a critical property for a gateway that will eventually handle thousands of concurrent LLM requests.

### Why Redis asyncio?
Consistent async programming model with the FastAPI/asyncpg stack. All I/O is non-blocking.

### Why Loguru over Python's `logging` module?
Loguru provides structured logging with minimal boilerplate, built-in JSON serialisation, log rotation, and colourised output — all in a single library with zero config.

### Why pydantic-settings for configuration?
Type-safe, validated, IDE-friendly settings with automatic environment variable loading. The `@lru_cache` singleton ensures `.env` is read exactly once.

### Why Alembic for migrations?
The only mature migration tool for SQLAlchemy. The async-compatible `env.py` ensures the same async engine is used for both the application and migrations.

---

## Future Phases Architecture

```
Phase 2 – Authentication
  └── ApiKey model, JWT middleware, tenant scoping

Phase 3 – Provider Adapters
  └── app/providers/{openai,gemini,anthropic,groq,ollama}.py
  └── Unified ProviderAdapter interface

Phase 4 – Routing Engine
  └── app/services/router.py – provider selection strategy
  └── Weight-based, cost-based, latency-based routing

Phase 5 – Reliability
  └── Circuit breakers (per provider)
  └── Retry policies with exponential backoff
  └── Rate limiting (Redis sliding window)

Phase 6 – Observability
  └── Prometheus metrics endpoint /metrics
  └── OpenTelemetry trace propagation
  └── Cost tracking per request/tenant

Phase 7 – Kubernetes
  └── Helm chart in infrastructure/helm/
  └── HorizontalPodAutoscaler
  └── PostgreSQL + Redis via Bitnami charts
```
