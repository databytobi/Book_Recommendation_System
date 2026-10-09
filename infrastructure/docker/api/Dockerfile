# syntax=docker/dockerfile:1
# ============================================================
# API PRODUCTION IMAGE
#
# Build context: repository root
#   docker build -f infrastructure/docker/api/Dockerfile .
# ============================================================

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# System dependencies:
#   libpq5        - runtime PostgreSQL client library (psycopg2)
#   libgomp1      - OpenMP runtime required by faiss-cpu and scikit-learn
#   gcc/g++       - build toolchain for source distributions
#   curl          - container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    libpq5 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for Docker layer caching.
COPY requirements.txt .
# Upgrade pip/setuptools first to avoid hash-mismatch issues with
# transitive dependencies (e.g. markdown_it_py/mdurl) that can occur
# when PyPI serves a newer wheel than pip's cache expects.
RUN pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir --default-timeout=300 --retries 10 -r requirements.txt

# Copy API application.
COPY apps/api /app

# Artifact directories. In production these are populated by the model
# training job and mounted as a volume; the mkdir guarantees the paths
# exist so lazy loading fails loudly rather than with a missing-directory error.
RUN mkdir -p \
    /app/ml/artifacts \
    /app/ml/models \
    /app/logs

# Run as an unprivileged user.
RUN useradd --create-home --uid 1001 --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/api/v1/health/liveness || exit 1

# Production server. `--workers 1` is deliberate: the ML service registry
# holds large in-process models, so multiple workers multiply memory use.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]