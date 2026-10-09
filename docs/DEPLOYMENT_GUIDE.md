# 🚀 Deployment Guide

**Target:** a single VPS or dedicated server running Docker Compose.
**Time to first deploy:** ~20 minutes (plus model artifact generation).

This guide covers a production deployment of the Hybrid Book Recommendation System on
one host. Everything below is exercised by the files in this repository — it is not
aspirational.

---

## Table of Contents

1. [Architecture of the deployment](#1-architecture-of-the-deployment)
2. [Server prerequisites](#2-server-prerequisites)
3. [First-time setup](#3-first-time-setup)
4. [Model artifacts (required first)](#4-model-artifacts-required-first)
5. [Starting the stack](#5-starting-the-stack)
6. [Database migrations](#6-database-migrations)
7. [TLS / HTTPS](#7-tls--https)
8. [Operations](#8-operations)
9. [Backups](#9-backups)
10. [Updating a deployment](#10-updating-a-deployment)
11. [Monitoring](#11-monitoring)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Architecture of the deployment

Only **nginx** publishes a port to the internet. Everything else communicates over the
internal `book_network` bridge, so PostgreSQL, Redis, the API, Grafana and Prometheus are
never directly reachable from outside the host.

```
                    Internet
                       │
              :80 / :443 (nginx)
                       │
        ┌──────────────┴──────────────┐
        │                             │
   /api/*, /docs,                everything else
   /health, /metrics                   │
        │                              │
   ┌────▼────┐                  ┌──────▼──────┐
   │   api   │                  │  frontend   │
   │  :8000  │                  │    :3000    │
   └────┬────┘                  └─────────────┘
        │
   ┌────┴─────────┬──────────────┐
   │              │              │
┌──▼───┐    ┌─────▼────┐   ┌─────▼───────┐
│postgres│  │  redis   │   │ ml_artifacts│
│ :5432  │  │  :6379   │   │  (volume)   │
└────────┘  └──────────┘   └─────────────┘
```

**What you need:** 4 GB RAM minimum (8 GB recommended), 2 vCPU, 40 GB disk.
The embedding index and model artifacts add roughly 1–2 GB.

---

## 2. Server prerequisites

Docker Engine 24+ with the Compose v2 plugin:

```bash
# Debian / Ubuntu
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
docker compose version
```

Open only the ports you need:

```bash
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw enable
```

---

## 3. First-time setup

### 3.1 Clone the repository

```bash
git clone <your-repo-url> book-recommendation
cd book-recommendation
```

### 3.2 Create the production environment file

```bash
cp .env.example .env
```

Generate strong secrets — **do not reuse the placeholders**:

```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))"
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(64))"
python3 -c "import secrets; print('ADMIN_API_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('REDIS_PASSWORD=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('GRAFANA_PASSWORD=' + secrets.token_urlsafe(24))"
```

Edit `.env` and set at minimum:

```env
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

SECRET_KEY=<generated value>
JWT_SECRET=<generated value>
ADMIN_API_KEY=<generated value>

POSTGRES_USER=postgres
POSTGRES_PASSWORD=<generated value>
POSTGRES_DB=book_recommendation_db
REDIS_PASSWORD=<generated value>

# Set this to the URL your browser will use.
NEXT_PUBLIC_API_URL=https://your-domain.example/api/v1
ALLOWED_ORIGINS=https://your-domain.example

GRAFANA_PASSWORD=<generated value>
GRAFANA_ROOT_URL=https://your-domain.example/grafana
```

> **The API will refuse to start** if `ENVIRONMENT=production` and `SECRET_KEY`/
> `JWT_SECRET` are empty, shorter than 32 characters, or still contain `CHANGE_ME`.
> The same applies to `DEBUG=True` and a wildcard `ALLOWED_ORIGINS`. This is deliberate —
> it is far better to fail at startup than to sign tokens with a public placeholder.

### 3.3 Lock down the environment file

```bash
chmod 600 .env
```

`.env` is git-ignored. Verify it is not tracked:

```bash
git check-ignore -v .env    # should print a .gitignore match
```

---

## 4. Model artifacts (required first)

The API loads a FAISS embedding index and an ALS model **from disk**. A fresh environment
must generate them before the API can serve recommendations.

The containers read artifacts from the `ml_artifacts` and `ml_models` volumes. The
`ml-train` service mounts the source and data so you can run the pipeline directly.

### 4.1 Place the raw datasets

```bash
mkdir -p data/raw/"Book-Crossing dataset" data/raw/"Goodreads dataset"
# copy Books.csv, Ratings.csv, Users.csv and the Goodreads books.csv into place
```

### 4.2 Run the pipeline in order

```bash
COMPOSE="docker compose -f infrastructure/compose/docker-compose.prod.yml --profile tools"

# 1. Clean the sources
$COMPOSE run --rm ml-train python scripts/data/scripts_cleaning/clean_books.py
$COMPOSE run --rm ml-train python scripts/data/scripts_cleaning/clean_ratings.py
$COMPOSE run --rm ml-train python scripts/data/scripts_cleaning/clean_users.py
$COMPOSE run --rm ml-train python scripts/data/scripts_cleaning/clean_goodreads.py

# 2. Integrate + validate
$COMPOSE run --rm ml-train python scripts/data/integration/merge_datasets.py
# Canonical dedup — writes master_books_deduplicated.parquet, the file training reads.
$COMPOSE run --rm ml-train python scripts/data/integration/deduplicate_catalog.py
$COMPOSE run --rm ml-train python scripts/data/integration/schema_validator.py

# 3. Build features
$COMPOSE run --rm ml-train python ml/features/embedding_pipeline.py
$COMPOSE run --rm ml-train python ml/features/interaction_matrix.py

# 4. Train
$COMPOSE run --rm ml-train python ml/collaborative/train_collaborative.py
$COMPOSE run --rm ml-train python ml/train_popularity.py

# 5. Evaluate
$COMPOSE run --rm ml-train python ml/evaluate_popularity.py
```

Verify the artifacts landed:

```bash
docker run --rm -v book_ml_artifacts:/a alpine ls -la /a | head -25
```

You should see `books_faiss.index`, `book_embeddings.npy`, `semantic_books.parquet`,
`als_model.pkl`, `user_encoder.pkl`, `book_encoder.pkl`.

> **Prefer to skip this?** If you already have a populated
> `apps/api/ml/artifacts/` locally, copy it straight into the volume instead:
>
> ```bash
> docker run --rm -v book_ml_artifacts:/a -v "$PWD/apps/api/ml/artifacts":/src alpine \
>   cp -a /src/. /a/
> ```

---

## 5. Starting the stack

```bash
docker compose -f infrastructure/compose/docker-compose.prod.yml up -d --build
```

Check status — every service should report `healthy`:

```bash
docker compose -f infrastructure/compose/docker-compose.prod.yml ps
```

The API container has a `start_period` of 60 seconds because loading the FAISS index
takes time.

Verify the deployment:

```bash
curl -fsS http://localhost/health
curl -fsS http://localhost/api/v1/health/liveness
curl -fsS http://localhost/api/v1/health/readiness
curl -fsS http://localhost/api/v1/recommendation/health
```

Then open `http://your-domain.example/` — you should see the login page.

---

## 6. Database migrations

The schema is managed by Alembic. Run migrations against the live database:

```bash
docker compose -f infrastructure/compose/docker-compose.prod.yml exec api \
  alembic upgrade head
```

To import the book catalog into PostgreSQL after the schema exists, use the bulk import
step described in `docs/millstone.md`.

---

## 7. TLS / HTTPS

The bundled `nginx.conf` serves plain HTTP on port 80. For production, terminate TLS at
nginx.

### Option A — Certbot on the host

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.example
```

Copy the certificates where nginx can read them, then uncomment the `443` port and the
`certs` volume in `docker-compose.prod.yml`, and add to the `server` block in
`nginx.conf`:

```nginx
listen 443 ssl;
ssl_certificate     /etc/nginx/certs/fullchain.pem;
ssl_certificate_key /etc/nginx/certs/privkey.pem;
ssl_protocols       TLSv1.2 TLSv1.3;
```

Add an HTTP→HTTPS redirect:

```nginx
server {
    listen 80;
    server_name your-domain.example;
    return 301 https://$host$request_uri;
}
```

Then reload:

```bash
docker compose -f infrastructure/compose/docker-compose.prod.yml restart nginx
```

### Option B — Cloudflare / external load balancer

Point the proxy at the host on port 80 and let it handle certificates. Set
`NEXT_PUBLIC_API_URL` and `ALLOWED_ORIGINS` to the public HTTPS origin.

---

## 8. Operations

```bash
COMPOSE="docker compose -f infrastructure/compose/docker-compose.prod.yml"

$COMPOSE ps                      # status
$COMPOSE logs -f api             # follow API logs
$COMPOSE logs -f nginx           # follow proxy logs
$COMPOSE restart api             # restart one service
$COMPOSE down                    # stop (keeps volumes)
$COMPOSE down -v                 # stop and DELETE all data
```

Useful API endpoints once running:

| Endpoint | Purpose |
|---|---|
| `GET /health` | Composite health |
| `GET /api/v1/health/readiness` | Ready to serve traffic |
| `GET /api/v1/recommendation/health` | ML recommender status |
| `GET /api/v1/recommendation/stats` | Recommender statistics |
| `GET /metrics` | Prometheus metrics |
| `GET /docs` | Swagger UI |
| `POST /admin/reload` | Reload ML services — requires `X-Admin-Key` |
| `GET /admin/registry` | ML registry detail — requires `X-Admin-Key` |

Operational endpoints require the admin key:

```bash
curl -X POST http://localhost/admin/reload \
  -H "X-Admin-Key: $ADMIN_API_KEY"
```

In staging/production these endpoints return **503** if `ADMIN_API_KEY` is unset,
and **401** if the header is missing or wrong.

---

## 9. Backups

**PostgreSQL** — the only stateful component that matters:

```bash
docker compose -f infrastructure/compose/docker-compose.prod.yml exec -T postgres \
  pg_dump -U postgres book_recommendation_db | gzip > backup-$(date +%F).sql.gz
```

Restore:

```bash
gunzip -c backup-2025-01-01.sql.gz | \
  docker compose -f infrastructure/compose/docker-compose.prod.yml exec -T postgres \
  psql -U postgres -d book_recommendation_db
```

Automate with a nightly cron job and copy backups off the host. Redis and the ML
artifacts are both reproducible and do not need backing up.

---

## 10. Updating a deployment

```bash
git pull origin main

COMPOSE="docker compose -f infrastructure/compose/docker-compose.prod.yml"

$COMPOSE build api frontend
$COMPOSE up -d
$COMPOSE exec api alembic upgrade head
```

If the ML artifacts changed, reload the recommender without a restart:

```bash
curl -X POST http://localhost/admin/reload -H "X-Admin-Key: $ADMIN_API_KEY"
```

> `NEXT_PUBLIC_API_URL` is baked into the frontend bundle at **build** time. If you
> change it, you must rebuild the frontend image — restarting is not enough.

---

## 11. Monitoring

Prometheus scrapes the API at `/metrics` every 15 seconds. Grafana is provisioned with
the datasource and dashboards and is reachable at `/grafana/` through nginx.

Key metrics:

| Metric | Meaning |
|---|---|
| `recommendations_generated_total` | Recommendations served, by type and status |
| `recommendation_requests_total` | Request volume by endpoint |
| `recommendation_errors_total` | Errors by endpoint and type |
| `recommendation_duration_seconds` | Generation latency histogram |
| `request_duration_seconds` | HTTP latency histogram |
| `cache_operations_total` | Cache hits and misses |

Set `GRAFANA_PASSWORD` in `.env` before first start. To disable monitoring entirely,
remove the `prometheus` and `grafana` services from the compose file.

---

## 12. Troubleshooting

**API exits immediately with a validation error**
A production safeguard fired. The message names the offending variable — usually
`SECRET_KEY`, `JWT_SECRET`, `DEBUG`, or `ALLOWED_ORIGINS`. See §3.2.

**`POSTGRES_PASSWORD is required` from docker compose**
`.env` is missing or unreadable. Confirm it exists at the repository root and contains
`POSTGRES_PASSWORD`.

**API is healthy but recommendations return 503**
The model artifacts are missing from the volume. Re-run §4, then
`curl -X POST http://localhost/admin/reload -H "X-Admin-Key: $ADMIN_API_KEY"`.

**`/admin/reload` returns 503**
`ADMIN_API_KEY` is not set. Admin endpoints are deliberately disabled in
production without it. Set it in `.env` and restart the API.

**`/admin/reload` returns 401**
The `X-Admin-Key` header is missing or does not match `ADMIN_API_KEY`.

**Frontend loads but every API call fails**
`NEXT_PUBLIC_API_URL` was wrong at build time. Fix `.env`, then
`docker compose ... build frontend && docker compose ... up -d frontend`.

**CORS errors in the browser console**
`ALLOWED_ORIGINS` must list the exact origin the browser uses, including scheme and port.

**`index ix_... already exists` during schema creation**
A model declares the same index twice. Fixed for the shipped models; if you add a new
one, use either `index=True` on the column **or** an explicit `Index()`, never both.

**Container is OOM-killed**
Loading the FAISS index is memory-hungry. Raise the host memory or add a `mem_limit`
to the `api` service.

### Deploy checklist

- [ ] `.env` created with generated secrets, `chmod 600`, git-ignored
- [ ] `ENVIRONMENT=production` and `DEBUG=False`
- [ ] `NEXT_PUBLIC_API_URL` and `ALLOWED_ORIGINS` set to the real domain
- [ ] Model artifacts present in the `ml_artifacts` volume
- [ ] `alembic upgrade head` run
- [ ] All services report `healthy`
- [ ] `/health` and `/api/v1/health/readiness` return 200
- [ ] TLS configured and HTTP redirected to HTTPS
- [ ] Nightly database backup scheduled
- [ ] Firewall exposes only 22, 80, 443