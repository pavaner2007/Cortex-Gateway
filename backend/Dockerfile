# ─────────────────────────────────────────────────────────────────────────────
# Cortex Gateway – Backend Dockerfile
# Multi-stage build: base → dependencies → development / production
# ─────────────────────────────────────────────────────────────────────────────

# ───────────────────────────────────────────
# Stage 1: Base image with OS dependencies
# ───────────────────────────────────────────
FROM python:3.12-slim AS base

WORKDIR /app

# Environment hardening
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install required system packages (curl for health checks)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# ───────────────────────────────────────────
# Stage 2: Install Python dependencies
# ───────────────────────────────────────────
FROM base AS dependencies

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# ───────────────────────────────────────────
# Stage 3: Development (hot-reload via volume mount)
# ───────────────────────────────────────────
FROM dependencies AS development

# Create log directory
RUN mkdir -p /app/logs

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "info"]

# ───────────────────────────────────────────
# Stage 4: Production (non-root, no volume mount)
# ───────────────────────────────────────────
FROM dependencies AS production

# Create non-root user for security
RUN groupadd -r cortex && useradd -r -g cortex -u 1000 cortex \
    && mkdir -p /app/logs \
    && chown -R cortex:cortex /app

COPY --chown=cortex:cortex . .

USER cortex

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--log-level", "warning"]
