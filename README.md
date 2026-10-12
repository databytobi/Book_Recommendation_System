# 📚 Hybrid Book Recommendation System

A full-stack book discovery platform: a FastAPI backend with a hybrid ML recommendation engine, a Next.js frontend, and a Dockerized infrastructure serving a catalog of **248,176 books** with personalized recommendations, semantic search, favorites, and reading history.

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)
![Redis](https://img.shields.io/badge/Redis-7-DC382D)
![FAISS](https://img.shields.io/badge/FAISS-vector_search-orange)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Tests](https://img.shields.io/badge/tests-46%20passed-brightgreen)

</p>

---

## Overview

Users register, complete a short onboarding (favorite authors, favorite books, reading style), and receive personalized recommendations from a hybrid engine that blends four signals: author affinity, popularity, reading style, and collaborative filtering.

The system runs **two complementary recommenders**:

| Endpoint | Engine | What it does |
|---|---|---|
| `/api/v1/recommendations` | **Catalog hybrid** | Scores catalog books for the logged-in user: FAISS semantic neighbors of their favorites, blended with author-match, popularity, reading-style, and collaborative signals. Falls back to most-rated books for brand-new accounts. |
| `/api/v1/recommendation/*` | **ML engine** | Trending, similar-books, semantic search, per-user batch recommendations, and score explanations, backed by the hybrid recommender (collaborative 0.50 / content 0.30 / popularity 0.20). |

### A note on the data architecture

**The book catalog lives in parquet, not PostgreSQL.** The `books` SQL table exists but is intentionally empty all 248k book records are read from `data/processed/integrated/master_books_deduplicated.parquet` (exposed to the API as the cached `semantic_books` artifact). Only *user* state (accounts, profiles, favorites, interactions) lives in Postgres. This is the single most important thing to know when working in this codebase: routes that read book metadata must go through the parquet catalog (`BookService`), never the `books` table.

---

## Features

- **Personalized recommendations**: hybrid scoring with human-readable reasons ("From one of your favorite authors", "Readers with similar taste enjoyed this")
- **Trending books**: popularity pool of 3,069 strongly-rated titles with category diversity so no single series dominates
- **Search**: title/author search across the full catalog, plus ML semantic search
- **Favorites & history**: persisted per user, validated against the catalog
- **Onboarding flow**: captures favorite authors, favorite books, reading style, and reading goals
- **Book covers**: served from Amazon's CDN with URL normalization (the legacy `images.amazon.com` host returns 403; URLs are rewritten to `images-na.ssl-images-amazon.com`)
- **Derived genres**: no source dataset contains genre data, so genres are inferred at read time (see [Known Limitations](#known-limitations))
- **JWT auth** — register/login/refresh, with a `user_profiles` row created at registration

---

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- ~4 GB RAM for the stack

### 1. Get the data (required it is git-ignored)

The catalog, ratings, and ML artifacts are **not in the repository**. You need:

1. The two raw datasets, placed under `data/raw/`:
   - **Book-Crossing dataset** (`Books.csv`, `Ratings.csv`, `Users.csv`)
   - **Goodreads dataset** (`books.csv`)
2. Run the data pipeline to produce `data/processed/`:
   - Cleaning: `scripts/data/scripts_cleaning/` — `clean_books.py`, `clean_goodreads.py`, `clean_ratings.py`, `clean_users.py`, `deduplicate_books.py`
   - Integration: `scripts/data/integration/` — `merge_datasets.py`, `schema_validator.py`, `deduplicate_catalog.py` (produces `data/processed/integrated/master_books_deduplicated.parquet`)
3. Generate the ML artifacts under `apps/api/ml/`:
   - `features/interaction_matrix.py` — the training interactions
   - `features/embedding_pipeline.py` — semantic embeddings + FAISS index (`semantic_books.parquet`)
   - `train_popularity.py` — the popularity recommender model

See [docs/PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md) for the full pipeline description.

### 2. Configure the environment

```bash
cp .env.example .env.docker   # then fill in real values (DB URL, JWT secrets)
```

`.env.docker` is the file Compose reads; it is git-ignored.

### 3. Run the stack

On Windows PowerShell, use the bundled helper:

```powershell
.\docker.ps1 up        # start the stack (build if needed)
.\docker.ps1 status    # container health
.\docker.ps1 logs      # follow API logs
.\docker.ps1 test      # quick API smoke test
.\docker.ps1 down      # stop the stack (keeps data)
.\docker.ps1 reset     # stop and DELETE all data/volumes
```

Or with plain Docker Compose:

```bash
docker compose -f infrastructure/compose/docker-compose.dev.yml up -d --build
```

### 4. Apply database migrations

The first start creates the database via `init-db.sql`, but the schema is managed by Alembic (12 tables: users, user_profiles, books, favorites, interactions, preferences, and related) and must be applied explicitly:

```bash
docker exec -w /app book_api alembic upgrade head
```

### 5. Open the app

| Service | URL |
|---|---|
| Frontend (Next.js) | http://localhost:3000 |
| API (FastAPI) | http://localhost:8000 |
| Interactive API docs (Swagger) | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

Default containers: `book_frontend`, `book_api`, `book_postgres`, `book_redis`.

---

## API Overview

All routes are versioned under `/api/v1`.

| Prefix | Purpose |
|---|---|
| `/auth` | Register, login, token refresh, current user |
| `/books` | Browse + search the 248k-book parquet catalog (with derived genres) |
| `/recommendations` | Personalized catalog recommendations (hybrid scoring) |
| `/recommendation` | ML engine: `/trending`, `/similar`, `/search`, `/user`, `/batch`, `/explain/{user_id}/{isbn}`, `/weights`, `/stats` |
| `/favorites` | Add / remove / list favorite books |
| `/history` | Reading history per user |
| `/onboarding` | Onboarding steps and status |
| `/authors` | Author listings and author-based recommendations |

Browse the live schema at http://localhost:8000/docs.

---

## Technology Stack

| Layer | Technology |
|---|---|
| API | Python 3.11, FastAPI 0.136, Pydantic v2, SQLAlchemy 2, Alembic |
| ML | FAISS (semantic retrieval), sentence-transformers, implicit (ALS), scikit-learn, pandas |
| Frontend | Next.js 16 (standalone output), React 19, Tailwind CSS v4, Base UI components |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Infra | Docker Compose (dev + prod), Nginx (prod), Prometheus/Grafana (profiles) |

---

## Repository Structure

```text
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── app/                #   application code (routers, models, services)
│   │   ├── alembic/            #   database migrations
│   │   ├── ml/                 #   ML pipeline: popularity, collaborative, content,
│   │   │                       #   hybrid, features, retrieval, models, artifacts
│   │   └── tests/              #   API test suite (46 tests)
│   ├── frontend/web/           # Next.js 16 app
│   └── ml/                     # legacy ML package (superseded by apps/api/ml)
├── data/                       # git-ignored: raw + processed datasets, parquet
├── docs/                       # architecture, deployment guide, risks, decisions
├── infrastructure/
│   ├── compose/                # docker-compose.dev.yml / docker-compose.prod.yml
│   └── docker/                 # API + frontend Dockerfiles, Nginx, Prometheus
├── scripts/data/               # dataset cleaning + integration pipeline
├── docker.ps1                  # Windows helper for the Docker workflow
└── .env.example                # environment template
```

---

## Development

### Running tests

```bash
docker exec -w /app book_api python -m pytest tests -q
```

Current state: **46 passed, 1 skipped, 0 failed**.

### Profiles (optional services)

```bash
docker compose -f infrastructure/compose/docker-compose.dev.yml --profile tools up -d
```

| Profile | Adds |
|---|---|
| `tools` (or `dev`) | pgAdmin Postgres admin UI at http://localhost:5050 |
| `ml` (or `training`) | One-shot ML training container |
| `monitoring` | Prometheus (9090), Grafana, node-exporter, cAdvisor |

### Production

`docker-compose.prod.yml` fronts everything through Nginx on port 80. See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md).

---

## Known Limitations

Being upfront about the current state of the system:

- **Genres are inferred, not sourced.** Neither raw dataset contains genre data. Genres are derived at read time in [`apps/api/app/core/genres.py`](apps/api/app/core/genres.py) using word-boundary keyword matching plus publisher-imprint rules. Coverage is ~24% of the catalog; the rest return `null`. Real coverage would require an external join (e.g. Open Library bulk dumps, with ISBN-13 normalization).
- **The popularity pool is 3,069 books** only ~3.3k of the 248k catalog entries carry rating counts from Goodreads. Trending cannot rank books with no rating data.
- **Notifications are mock data.** The bell dropdown renders placeholder entries; there is no notifications backend.
- **Search filters are not implemented.** The search UI accepts filters, but the API currently only supports free-text query.
- **No password reset or email verification flow** — verification codes are generated but not sent.

---

## Documentation

- [PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md): full project reference
- [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md): Docker and production deployment
- [RISKS.md](docs/RISKS.md): known risks, including the missing genre column
- [technical_decisions.md](docs/technical_decisions.md): architecture decisions
- [METRICS.md](docs/METRICS.md) / [SUCCESS_METRICS.md](docs/SUCCESS_METRICS.md): quality metrics

---

## License

No license file has been added yet. All rights reserved until one is chosen.
