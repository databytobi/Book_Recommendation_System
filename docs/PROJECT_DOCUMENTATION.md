# 📚 Hybrid Book Recommendation System — Project Documentation

**Version:** 1.0.0 · **Last updated:** documentation pass over the current working tree
**Repository:** `Book Recommendation System` · **Status:** active development (API + frontend functional; ML pipeline has known gaps — see §11)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Vision](#2-problem-statement--vision)
3. [Technology Stack](#3-technology-stack)
4. [System Architecture](#4-system-architecture)
5. [Repository Layout](#5-repository-layout)
6. [Backend — Application Layer](#6-backend--application-layer)
7. [API Reference](#7-api-reference)
8. [Data Model](#8-data-model)
9. [Machine Learning & Recommendation Engine](#9-machine-learning--recommendation-engine)
10. [Data Pipeline](#10-data-pipeline)
11. [Known Gaps & Technical Debt](#11-known-gaps--technical-debt)
12. [Setup & Running Locally](#12-setup--running-locally)
13. [Testing](#13-testing)
14. [Deployment & Infrastructure](#14-deployment--infrastructure)
15. [Observability](#15-observability)
16. [Glossary](#16-glossary)

---

## 1. Executive Summary

The Hybrid Book Recommendation System is a full-stack platform that recommends books to readers the way
Spotify recommends music — by combining several independent recommendation signals rather than relying on
bestseller lists or manual curation.

The system is built as a **modular monolith**: one FastAPI application containing a cleanly separated
API / service / repository / ML-service stack, backed by PostgreSQL, Redis, a FAISS vector index, and
serialized model artifacts. A Next.js 16 App Router frontend consumes the REST API.

**What exists today:**

| Area | State |
|---|---|
| REST API | Implemented — auth, books, authors, favorites, history, onboarding, recommendations, health, monitoring |
| Authentication | Implemented — JWT access/refresh, bcrypt password hashing, email verification, password reset |
| Database models | Implemented — 12 SQLAlchemy models covering users, catalog, interactions, preferences, events |
| Hybrid recommender | Implemented — weighted fusion of collaborative + content + popularity with graceful degradation |
| Content/semantic search | Implemented — 248,176 books embedded at 384 dimensions in a FAISS cosine index |
| Collaborative filtering | Implemented — implicit ALS (64 factors) with persisted encoders |
| Popularity engine | Implemented — adjusted-score ranking with category-diversity and recency weighting |
| Frontend | Implemented — 14 routes, auth flows, dashboard shell, typed API client |
| Observability | Implemented — Prometheus metrics, Grafana provisioning, in-app monitor, health probes |
| CI/CD | Partial — workflows defined but contain broken paths (see §11) |
| Deployment | Not yet functional — `DEPLOYMENT_GUIDE.md` is a stub; the compose `deploy` job only echoes |

> **Architecture diagrams (SVG):**
> - [`docs/architecture/architecture-overview.svg`](architecture-overview.svg) — layered system architecture
> - [`docs/architecture/ml-data-pipeline.svg`](ml-data-pipeline.svg) — data → features → training → serving
> - [`docs/architecture/request-flow.svg`](request-flow.svg) — runtime sequence of one recommendation request

---

## 2. Problem Statement & Vision

Online book catalogs contain millions of titles spanning countless genres, authors, languages and themes.
Traditional search requires users to already know what they want, which produces **information overload**
and pushes discovery toward the same small set of bestsellers for every reader.

The project's stated vision (`PROJECT_VISION.md`) is to address two specific failure modes:

- **Repetitive recommendations** — the same popular titles surfaced indefinitely.
- **Generic recommendations** — suggestions that ignore an individual's evolving taste.

The target users are book lovers who want a platform that "knows them" — served well both when they arrive
with a rich reading history and when they are brand new with no history at all.

**Goals**

*Primary:* scalable engine · personalized output · multiple combined algorithms · production-ready backend ·
REST API surface for clients · headroom for growth.

*Secondary:* semantic discovery · explainable recommendations · real-time personalization · continuous model
improvement · cloud-native deployment.

---

## 3. Technology Stack

### Backend
| Component | Technology | Version (from `requirements.txt`) |
|---|---|---|
| Language | Python | 3.11 (Docker) / 3.12 (black target, `ci.yml`) |
| Framework | FastAPI | 0.136.1 |
| ASGI server | Uvicorn | 0.49.0 |
| ORM | SQLAlchemy | 2.0.50 |
| Validation | Pydantic / pydantic-settings | 2.13.4 / 2.14.1 |
| Migrations | Alembic | 1.13.3 |
| Auth | python-jose (JWT), passlib + bcrypt | — |
| Database driver | psycopg2-binary, asyncpg | 2.9.12 / 0.31.0 |
| Cache client | redis | 8.0.0 |

### Machine Learning
| Component | Technology | Notes |
|---|---|---|
| Embeddings | sentence-transformers | 5.5.1 · `all-MiniLM-L6-v2` · 384-dim |
| Vector search | faiss-cpu | 1.14.3 · `IndexFlatIP` (cosine via L2-normalised vectors) |
| Collaborative | implicit | 0.7.3 · Alternating Least Squares |
| Classical ML | scikit-learn | 1.9.0 · TF-IDF, cosine similarity, LabelEncoder |
| Numerics | numpy / scipy / pandas | 2.4.6 / 1.16.3 / 3.0.3 |
| Columnar IO | pyarrow | 24.0.0 (parquet artifacts) |
| Metrics | prometheus-client | 0.25.0 |

### Frontend
| Component | Technology | Version |
|---|---|---|
| Framework | Next.js (App Router) | 16.2.10 |
| UI library | React / react-dom | 19.2.4 |
| Language | TypeScript | ^5 |
| Styling | Tailwind CSS | ^4 (`@tailwindcss/postcss`) |
| Components | shadcn (`base-nova` style) + `@base-ui/react` | ^4.13.0 / ^1.6.0 |
| Forms | react-hook-form | ^7.86.0 |
| Icons / toasts / command | lucide-react, sonner, cmdk | — |
| Data fetching | Native `fetch` wrapper | `axios` is declared but unused |
| State | React Context only | `store/` and `providers/` are empty directories |

### Infrastructure
Docker · Docker Compose · PostgreSQL 16-alpine · Redis 7-alpine · Prometheus · Grafana · GitHub Actions.

---

## 4. System Architecture

### 4.1 Architectural style

A **modular monolith** designed so that modules can later be extracted into services with minimal
refactoring. Layers are strictly separated:

```
Presentation   → Next.js App Router (client components, route groups, dashboard shell)
Application    → FastAPI routers → services → repositories (SQLAlchemy)
Recommendation → MLServiceRegistry → popularity | content | collaborative → HybridRecommender
Data           → PostgreSQL · Redis · FAISS index · model artifacts
```

Each layer depends only downward. Routers never touch the database directly; they delegate to services and
repositories, and obtain ML components through the service registry.

### 4.2 Tier breakdown

**Client tier** — Next.js 16 App Router with three route groups: `(auth)` for login/register,
`(protected)` for onboarding, and `dashboard` for the ten authenticated application pages. Authentication
state lives in a React Context (`AuthProvider`); tokens persist in `localStorage` through a `tokenStorage`
singleton. There is no Redux, Zustand, or React Query — all server data is fetched through a hand-written
`fetch` wrapper in `lib/api/client.ts`.

**Application tier** — a single FastAPI process. On startup the `lifespan` context manager (1) initialises
monitoring services, (2) validates ML artifacts via `ArtifactValidator`, and (3) creates the
`MLServiceRegistry` in *lazy* mode so the process binds quickly and heavy models load on first use. A
`CORSMiddleware`, a `MonitoringMiddleware`, and an `@app.middleware("http")` logging hook wrap every request;
a global exception handler returns a consistent JSON error envelope.

**Recommendation tier** — `MLServiceRegistry` is the single seam between the API and the ML code. It holds
one instance each of `PopularityService`, `ContentService`, `CollaborativeService` and `HybridRecommender`,
and exposes `load_all()`, `reload()`, `reload_service()`, `health()` and `get_stats()`. The
`HybridRecommender` is the orchestrator: it calls the three services, normalises each score vector to
`[0,1]`, and fuses them with configurable weights.

**Data tier** — PostgreSQL holds transactional and user-facing state; Redis is the cache tier (256 MB,
`allkeys-lru`, AOF persistence); FAISS and the pickled models are file-based artifacts mounted as a Docker
volume.

### 4.3 Hybrid scoring model

Set in `app/core/config.py` and in `HybridRecommender.__init__`, weights are validated to sum to 1 (and
renormalised with a warning if they do not):

```
hybrid_score = 0.50 × collaborative + 0.30 × content + 0.20 × popularity
```

Each component is min-max normalised before fusion. Both `app/core/config.py` and
`app/api/v1/recommendations/service.py` implement scoring; the latter is a *database-driven* variant using
genre (0.30), author (0.25), popularity (0.15), reading-style bonus (0.10) and collaborative overlap (0.20),
and it attaches a human-readable `recommendation_reason` to each result.

### 4.4 Resilience design

The hybrid recommender is explicitly failure-tolerant:

- If the collaborative model has no data for a user, it **falls back to the popularity engine**.
- If content recommendations raise, the error is caught and `content_score` stays `0.0`.
- If popularity metadata is unavailable, the collaborative score still produces a ranking.
- `MLServiceRegistry.load_all()` loads each of the four services inside its own `try/except`, so one
  failure does not prevent the others from loading; per-service status is tracked and exposed via `/health`.

### 4.5 Caching strategy

Three layers:

1. **In-process recommender cache** — `HybridRecommender._cache`, keyed `user_{id}_{top_k}`, TTL 3600 s,
   cleared when it exceeds 100 entries.
2. **Service-level caches** — `ContentService` and `CollaborativeService` each maintain their own result
   caches.
3. **Redis** — the infrastructure cache tier configured via `REDIS_URL` / `REDIS_CACHE_TTL`.
4. **Artifact memoisation** — `ml/artifacts/cache.py` uses `@lru_cache(maxsize=1)` around FAISS index,
   embedding matrix, and semantic book frame loading, so the 248k-vector index is read from disk once.

---

## 5. Repository Layout

```
Book Recommendation System/
├── apps/
│   ├── api/                          # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py               # app factory, lifespan, middleware, app-level endpoints
│   │   │   ├── api/v1/               # routers: auth, authors, books, favorites, health,
│   │   │   │                         #          history, onboarding, recommendation, recommendations
│   │   │   ├── core/                 # config, database, security, logging, exceptions,
│   │   │   │                         # handlers, redis, artifact_validator
│   │   │   ├── models/               # 12 SQLAlchemy models
│   │   │   ├── repositories/         # BaseRepository + author/user preference/follow repos
│   │   │   ├── schemas/              # Pydantic request/response models
│   │   │   ├── services/             # auth, author, discovery, preference_builder, cache,
│   │   │   │                         # monitoring, recommendation_metrics, recommendation_monitor
│   │   │   └── middleware/           # request_logging
│   │   ├── ml/
│   │   │   ├── service_registry.py   # MLServiceRegistry singleton
│   │   │   ├── popularity/           # popularity_service, popularity_recommender
│   │   │   ├── content/              # content_service, content_recommender
│   │   │   ├── collaborative/        # collaborative_service, collaborative_recommender, train_
│   │   │   ├── hybrid/               # hybrid_recommender, hybrid_service
│   │   │   ├── features/             # embedding_pipeline, interaction_matrix
│   │   │   ├── retrieval/            # faiss_retriever
│   │   │   ├── evaluation/           # metrics, evaluator
│   │   │   ├── recommenders/         # BaseRecommender ABC
│   │   │   ├── artifacts/            # FAISS index, embeddings, parquet, pickles + cache.py
│   │   │   └── models/               # (empty — popularity models actually live in apps/ml/models)
│   │   ├── alembic/                  # migrations
│   │   └── tests/                    # pytest suite
│   └── frontend/web/                 # Next.js 16 App Router client
│       ├── app/                      # routes: (auth), (protected), dashboard/*
│       ├── components/               # dashboard, books, book-details, search, library,
│       │                             # reading, recommendations, onboarding, auth, ui
│       ├── features/auth/            # AuthProvider, context, hooks, schema, service
│       ├── hooks/                    # books, dashboard, reading, recommendations, search, user
│       ├── lib/                      # api client, mappers, adapters, mock data, types, services
│       └── services/storage/         # tokenStorage
├── scripts/data/
│   ├── scripts_cleaning/             # clean_books, clean_ratings, clean_users, clean_goodreads,
│   │                                 # deduplicate_books, config, utils
│   ├── integration/                  # merge_datasets, deduplicate_catalog, schema_validator
│   └── profiling/                    # sweetviz profiling
├── data/
│   ├── raw/                          # Book-Crossing dataset/, Goodreads dataset/
│   └── processed/                    # books/, ratings/, users/, goodreads/, integrated/
├── infrastructure/
│   ├── compose/                      # docker-compose.dev.yml, init-db.sql
│   └── docker/{api,frontend}/        # Dockerfiles, prometheus.yml, grafana provisioning
├── docs/                             # architecture/, datasets.md, METRICS.md, millstone.md, …
├── reports/profiling/                # generated sweetviz HTML
├── alembic/                          # root-level migration mirror
├── conftest.py · pytest.ini · requirements.txt · alembic.ini · .env · .env.docker
```

> Several root directories — `middleware/`, `repositories/`, `utils/`, `logs/`, `data/artifacts/`,
> `data/feature_store/`, `data/interim/` — exist but are **empty**. See §11.

---

## 6. Backend — Application Layer

### 6.1 Application entry point (`app/main.py`)

`main.py` performs a `sys.path` insertion so that `ml.*` imports resolve from `apps/api`, then constructs the
FastAPI app with a `lifespan` handler, custom OpenAPI metadata (logo, contact, MIT licence, tag
descriptions), and the following middleware chain:

| Order | Middleware | Responsibility |
|---|---|---|
| 1 | `CORSMiddleware` | `ALLOWED_ORIGINS` / `METHODS` / `HEADERS` from settings |
| 2 | `MonitoringMiddleware` | Auto-instruments every request |
| 3 | `@app.middleware("http")` | Logs method, path, status, duration; emits metrics; sets `X-Process-Time` |

A global `@app.exception_handler(Exception)` returns `{error, detail, path, timestamp}`.

**App-level endpoints** (outside `/api/v1`): `/` · `/health` · `/info` · `/version` · `/artifacts` ·
`/metrics` · `/monitor/metrics` · `/monitor/summary` · `/monitor/alerts` (GET + DELETE) ·
`/admin/reload` · `/admin/registry`.

### 6.2 Configuration (`app/core/config.py`)

Pydantic `BaseSettings` class `Settings` with environment-variable overrides. Env-file resolution order is
`.env.{ENVIRONMENT}` → `.env` → `.env.docker`. Validators enforce a legal `LOG_LEVEL`, a legal
`ENVIRONMENT`, and `postgresql://` / `redis://` URL schemes.

Key groups: **app** (`APP_NAME`, `APP_VERSION`, `API_V1_PREFIX`, `DEBUG`, `LOG_LEVEL`, `ENVIRONMENT`),
**database** (`DATABASE_URL`, pool size/overflow/echo), **redis** (`REDIS_URL`, `REDIS_CACHE_TTL`),
**security** (`SECRET_KEY`, `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_EXPIRATION_MINUTES`), **CORS**,
**paths** (`ARTIFACTS_DIR`, `MODELS_DIR`, `DATA_DIR`), and **recommender** (the three hybrid weights,
`MIN_RATINGS_THRESHOLD`, `DEFAULT_TOP_K`).

### 6.3 Database (`app/core/database.py`)

A single SQLAlchemy engine from `settings.DATABASE_URL`, a `SessionLocal` sessionmaker
(`autocommit=False`, `autoflush=False`), a declarative `Base`, and a `get_db()` FastAPI dependency that
yields a session and closes it in a `finally` block.

### 6.4 Security (`app/core/security.py`)

- `TokenType` enum: `access`, `refresh`, `reset_password`, `email_verification`; `TokenStatus`:
  `valid`, `expired`, `invalid`, `malformed`.
- bcrypt password hashing via `passlib.CryptContext`; policy constants for min/max length and complexity.
- JWT creation/validation via `python-jose` with configurable algorithm (`HS256`) and expiry (1440 minutes
  default = 24 h); refresh tokens live 30 days.
- `SecurityConfig` falls back to a placeholder secret if none is configured — **must be overridden in
  production**.

### 6.5 Repository layer (`app/repositories/`)

`BaseRepository[T]` provides generic `create`, `get_by_id`, `update`, `delete` (soft-delete aware via
`is_active`), `list` (with `skip`/`limit`/`include_inactive` and arbitrary keyword filters), `count`, and
`exists`. Specialised repositories: `AuthorRepository`, `UserPreferenceRepository`,
`UserFollowedAuthorRepository`.

### 6.6 Service layer (`app/services/`)

| Service | Responsibility |
|---|---|
| `auth_service.py` | Registration, login, refresh, logout, password reset, email verification |
| `author_service.py` | Author CRUD, search, trending/popular/prolific ranking |
| `author_discovery_service.py` | Discovery sections and follow recommendations |
| `preference_builder.py` | Derives structured preferences from onboarding + interaction history |
| `cache_service.py` | Cache abstraction |
| `monitoring.py` | Request/recommendation logging, health snapshot, log flushing |
| `recommendation_metrics.py` | Prometheus counters, histograms, gauges + `track_*` decorators |
| `recommendation_monitor.py` | Rolling latency/error metrics, alert thresholds, summaries |

---

## 7. API Reference

All versioned routes are mounted under **`/api/v1`**. Interactive docs at `/docs` (Swagger UI) and
`/redoc`; machine-readable schema at `/openapi.json`.

### Authentication — `/api/v1/auth`
| Method | Path | Purpose |
|---|---|---|
| POST | `/register` | Create an account |
| POST | `/login` | Authenticate, return access + refresh tokens |
| POST | `/refresh` | Exchange a refresh token |
| POST | `/logout` | Invalidate session |
| POST | `/password-reset` | Request a reset link |
| POST | `/confirm-password-reset` | Complete the reset |
| POST | `/verify-email` | Verify an email address |
| POST | `/resend-verification` | Re-send verification |
| GET | `/me` | Current authenticated user |

### Recommendations — `/api/v1/recommendation`
| Method | Path | Purpose |
|---|---|---|
| POST | `/user` | Personalized recommendations for a user |
| GET | `/user` | Same, query-parameter form |
| POST | `/similar` | Books similar to a given ISBN |
| POST | `/search` | Semantic / natural-language search |
| GET | `/trending` | Trending and popular books |
| GET | `/explain` | Explanation for a recommendation |
| GET | `/health` | Recommender health |
| GET | `/stats` | Recommender statistics |
| POST | `/reload` | Reload the recommender (admin) |
| PUT | `/weights` | Update hybrid weights (admin) |
| POST | `/batch` | Batch recommendations for many users |

### Other versioned routers
| Prefix | Endpoints |
|---|---|
| `/api/v1/books` | `GET /` browse · `GET /search` |
| `/api/v1/authors` | list, search, autocomplete, popular, top-rated, most-prolific, featured, trending, random, recommendations, follow/unfollow, bulk-follow, followed list, onboarding discovery, discovery, stats, follow-stats, CRUD, health |
| `/api/v1/favorites` | `GET /` · `POST /{isbn}` · `DELETE /{isbn}` |
| `/api/v1/history` | `GET /` reading history |
| `/api/v1/onboarding` | complete, save progress, status, skip, complete-step, preferences, reset, health |
| `/api/v1/recommendations` | `GET /` (database-driven personalized variant) |
| `/api/v1/health` | liveness, readiness, details, ml-services, root health |

> **Duplicate surface:** two recommendation routers exist — `recommendation` (ML-backed, richer) and
> `recommendations` (DB-backed, simpler). Both are mounted. See §11.

---

## 8. Data Model

Twelve SQLAlchemy models are registered in `app/models/__init__.py`:

| Model | Table | Purpose |
|---|---|---|
| `User` | `users` | Auth identity: username, email, bcrypt hash, full name, `is_active`, `is_superuser`, timestamps, `last_login`, preferences JSON |
| `Author` | `authors` | Author profile: bio, image, birth/death dates, nationality, website, Wikipedia, popularity score, `total_books`, `average_rating` |
| `Book` | `books` | Catalog: ISBN PK, title, authors, genre, publisher, publication year/date, language, pages, average rating, ratings/reviews counts, image URLs |
| `UserProfile` | `user_profiles` | Reading personality, reading speed, books/year, favourite genres, reading style, discovery preference |
| `UserPreference` | `user_preferences` | Typed preference records (`PreferenceCategory`, `PreferenceDataType`) + `PreferenceManager` |
| `UserBookInteraction` | `user_book_interactions` | Views, clicks, ratings, reviews, saves, shares, reading status, progress, time spent, source |
| `UserFavoriteBook` | `user_favorite_books` | Favourites with status, priority, named collections |
| `UserFollowedAuthor` | `user_followed_authors` | Author follows with status, notification preference, source |
| `SearchHistory` | `search_history` | Query log for search personalization |
| `RecommendationEvent` | `recommendation_events` | Impression/click telemetry for ranking feedback |
| `RecommendationClick` | `recommendation_clicks` | Click-level attribution |
| `UserBookInteraction` enums | — | `InteractionType`, `ReadingStatus`, `InteractionSource` |

**Book indexes:** `ix_books_title_author` (title), `ix_books_rating_popularity` (average_rating,
ratings_count), plus single-column indexes on ISBN, genre, language_code, average_rating, ratings_count.

Migrations live in both `alembic/versions/` and `apps/api/alembic/versions/` (mirrored). Known revisions:
`941fd45aea84` (initial), `7d3e579e7f23` (create books table), `bfbffd008889` (add reading style to user
profiles).

---

## 9. Machine Learning & Recommendation Engine

### 9.1 Service registry

`MLServiceRegistry` (`ml/service_registry.py`) is a lazily-initialised singleton holding the four services.
It tracks per-service `loaded` / `health_status` / `load_time` / `error`, supports full and selective
reload, and exposes `health()` and `get_stats()`. Convenience accessors (`get_popularity_service`,
`get_content_service`, `get_collaborative_service`, `get_hybrid_recommender`) raise `RuntimeError` when a
service is unavailable.

### 9.2 Popularity engine

`PopularityRecommender(BaseRecommender)` with `min_ratings=50`, `diversity_weight=0.3`,
`recency_weight=0.2`. It computes an adjusted ranking score (Bayesian shrinkage toward the global mean),
extracts category labels, applies category-diversity re-ranking, and applies recency weighting. Exposed via
`PopularityService`: `homepage()`, `trending()`, `category()`, `cold_start()`, `explain()`,
`get_popular_books()`, `refresh_model()`, `get_stats()`.

This is the **cold-start fallback** for the entire system.

### 9.3 Content engine

`ContentService` wraps `ContentRecommender` + `FaissRetriever`:

- Text features: `title. authors. publisher. language_code`
- Encoder: `sentence-transformers/all-MiniLM-L6-v2`, 384 dimensions, batch size 256
- Normalisation: L2 via `sklearn.preprocessing.normalize`, cast to `float32`
- Index: `faiss.IndexFlatIP` — inner product over unit vectors is exactly cosine similarity
- Scale: **248,176 books indexed**

Capabilities: `recommend_by_isbn`, `recommend_by_title`, `recommend_by_description`, `similar_books`,
`explain`, `explain_by_isbn`, `get_book_info`, `get_similarity`, `get_statistics`. Results are cached.

Artifacts: `semantic_books.parquet`, `book_embeddings.npy`, `books_faiss.index`, `embedding_metadata.pkl`.

### 9.4 Collaborative engine

`CollaborativeService` wraps `CollaborativeRecommender`, which loads an ALS model trained with
`implicit.als.AlternatingLeastSquares`:

| Hyperparameter | Value |
|---|---|
| `factors` | 64 |
| `regularization` | 0.05 |
| `iterations` | 20 |
| `random_state` | 42 |
| `confidence_scale` | 1.0 |
| `min_ratings_per_user` / `_per_item` | 5 |
| `test_size` | 0.2 |

Confidence is `book_rating × confidence_scale` floored at 1.0. User and item IDs are encoded with
`LabelEncoder` (`user_encoder.pkl`, `book_encoder.pkl`) so inference can translate between raw IDs and
matrix indices.

Capabilities: `recommend_for_user`, `get_user_history`, `similar_books`, `similar_users`,
`explain_recommendation`, plus `get_stats` / `health_check` / `refresh`.

### 9.5 Hybrid orchestrator

`HybridRecommender` is the fusion layer. For a personalized request it:

1. Checks the in-process cache (`user_{id}_{top_k}`, TTL 3600 s).
2. Requests `top_k × 3` collaborative candidates (extra headroom for normalisation).
3. **If collaborative is empty → returns popularity homepage results** (cold start).
4. Fetches the user's top-5 history, takes the highest-rated title, and queries the content engine
   (`top_k × 2`).
5. Min-max normalises `collab_score`, `content_score`, `popularity_score` (the last from `adjusted_score`
   or `log1p(ratings_count)`).
6. Computes `0.50·collab + 0.30·content + 0.20·popularity`, applies `min_score` and `exclude_authors`,
   sorts, truncates to `top_k`, and assigns `rank`.
7. Caches and returns.

Also provides `recommend_similar_books`, `search_and_recommend`, `cold_start_recommendations`,
`explain_recommendation`, `get_stats`, `health_check`, `refresh`.

### 9.6 Evaluation

`ml/evaluation/metrics.py` implements a complete offline metric suite:

*Core ranking:* `precision_at_k`, `recall_at_k`, `hit_rate_at_k`, `average_precision`, `map_at_k`,
`dcg_at_k`, `ndcg_at_k`, `mrr_at_k`.

*Beyond accuracy:* `catalog_coverage`, `item_coverage`, `diversity`, `novelty`, `serendipity`.

*Orchestration:* `evaluate_recommendations(...)` returns a metrics dict; `print_metrics(...)` pretty-prints
grouped output.

`RecommendationEvaluator` (`evaluator.py`) adds `sample_users`, `build_holdout`, `evaluate_user`,
`evaluate_model`, `cross_validate`, `evaluate_with_ground_truth`, and `compare_models`.
`evaluate_popularity.py` runs a non-personalized baseline against a held-out split.

---

## 10. Data Pipeline

### 10.1 Sources

| Dataset | Location | Files | Role |
|---|---|---|---|
| Book-Crossing | `data/raw/Book-Crossing dataset/` | `Books.csv` (71 MB), `Ratings.csv` (22 MB), `Users.csv` (10 MB) | Ratings, users, popularity signal |
| Goodreads | `data/raw/Goodreads dataset/` | `books.csv` (1.5 MB) | Rich metadata enrichment |

### 10.2 Cleaning (`scripts/data/scripts_cleaning/`)

| Script | Input | Output | Key transformations |
|---|---|---|---|
| `clean_books.py` | Book-Crossing `Books.csv` (latin-1) | `books/books_cleaned.{csv,parquet}` | Column normalisation; text/author/publisher normalisation; year cleaning; drop null & duplicate ISBNs |
| `clean_ratings.py` | `Ratings.csv` | `ratings/ratings_cleaned`, `ratings_explicit`, `ratings_implicit` | Deduplicate on (user, isbn); split explicit (>0) vs implicit (==0) |
| `clean_users.py` | `Users.csv` | `users/users_cleaned.{csv,parquet}` | Age cleaning; country extraction from free-text location (~100-entry mapping + comma fallback); `pycountry` ISO-2/ISO-3 enrichment |
| `clean_goodreads.py` | Goodreads `books.csv` (utf-8) | `goodreads/goodreads_cleaned.{csv,parquet}` + `language_summary.csv` | 3-tier resilient CSV parsing; ISBN cleanup; ~60 language codes → MARC-3; date parsing → `publication_year`; numeric coercion |

### 10.3 Integration (`scripts/data/integration/`)

`merge_datasets.py` standardises ISBNs on every frame (strip quotes/hyphens, uppercase), performs a
**LEFT JOIN of books ← goodreads on `isbn`** with `suffixes=('_bx','_gr')` (Goodreads values win where both
exist), derives `rating_category` and `is_english`, and writes `integrated/master_books.{parquet,csv}`.
Ratings whose ISBN is absent from the catalog are diverted to `integrated/orphan_ratings.*`.

`schema_validator.py` is a read-only quality gate: duplicate checks, coverage percentages (title, author,
publisher, language, rating, country), matrix sparsity, interactions per user/book, and a **10-point
readiness score** — `≥ 7` means "ready for hybrid recommendations".

Catalog de-duplication is provided by two scripts — `deduplicate_books.py` (quality-score ranking) and
`deduplicate_catalog.py` (title|author composite key). Both write
`integrated/master_books_deduplicated.{parquet,csv}`. They are **alternative strategies, not sequential
stages** (§11).

### 10.4 Feature engineering (`apps/api/ml/features/`)

**`embedding_pipeline.py`** — builds `semantic_text`, encodes with `all-MiniLM-L6-v2`, L2-normalises,
builds `faiss.IndexFlatIP`, and exports the four semantic artifacts. Finishes with three smoke-test queries.

**`interaction_matrix.py`** — reads `ratings_explicit.parquet`, keeps users with ≥ 5 interactions, splits
20 % held-out (`random_state=42`), builds a `scipy.sparse.csr_matrix`, and exports the train/test frames,
matrix, index mappings, and stats.

### 10.5 Training (`apps/api/ml/`)

`train_collaborative.py` → `als_model.pkl`, encoders, `interaction_matrix.npz`,
`collaborative_metadata.pkl`, `train_ratings.parquet`.

`train_popularity.py` → `popularity_recommender.pkl`, `popularity_recommender_enhanced.pkl`,
`popularity_scores.parquet`.

### 10.6 Offline → online boundary

The batch path is re-run whenever the catalog, ratings, or embedding model changes. The online API only ever
reads the resulting artifacts — loaded lazily and memoised via `@lru_cache` in `ml/artifacts/cache.py` — and
never touches the raw datasets.

---

## 11. Known Gaps & Technical Debt

This section records concrete, verified issues found during the documentation and
hardening passes. Every row below was **reproduced**, then fixed, then **re-verified**.

**Verification baseline after hardening**

| Check | Result |
|---|---|
| Test suite | **46 passed, 1 skipped, 0 failed** (was 33 passed / 13 failed) |
| `ruff check apps/api` | **All checks passed** (focused correctness rules) |
| `black --check` | Config valid; repository not yet fully formatted (informational in CI) |
| `npx tsc --noEmit` (frontend) | **Clean** |
| `docker compose config` (prod) | **Valid**; fails fast on missing `POSTGRES_PASSWORD` as intended |
| ML service registry | **4/4 healthy** — popularity, content, collaborative, hybrid |
| App import | **79 routes**, 0 OpenAPI operationId collisions |
| Pipeline input resolution | **8/8 required inputs found** |

### 11.1 Pipeline correctness

| # | Issue | Status |
|---|---|---|
| 1 | `train_popularity.py` used the absolute POSIX path `/data/processed` | **Fixed** — resolves via `ml/paths.py` |
| 2 | `embedding_pipeline.py`, `interaction_matrix.py`, `content_service.py`, `collaborative_service.py` computed `BASE_DIR = parents[1]`, doubling path segments (`apps/api/ml/apps/api/ml/artifacts`) | **Fixed** — all use `ml/paths.py` |
| 3 | `evaluate_popularity.py` imported the non-existent `mean_average_precision_at_k` | **Fixed** — now imports `map_at_k` |
| 4 | Two de-duplication scripts wrote the same output with different strategies | **Fixed** — `deduplicate_catalog.py` is canonical; the ISBN-only variant writes `*_by_isbn.parquet` |
| 5 | Model `.pkl` files lived in `apps/ml/models/` while the service read `apps/api/ml/models/` | **Fixed** — service searches both locations plus artifacts |
| 6 | `merge_datasets.py` loaded the users frame but never joined it | **Resolved as intended** — documented; joining a reader-level frame into a book-level table would fan out rows. Users are validated separately by `schema_validator.py` |
| 7 | `master_books` has **no `genre` column** | **Fixed** — genre scoring removed and remaining signals re-weighted (author 0.4167, popularity 0.2500, style 0.1667, collaborative 0.1666) |
| 8 | `PROJECT_ROOT`/`BASE_DIR` referenced in `embedding_pipeline.py` and `interaction_matrix.py` debug blocks without being defined (`NameError`) | **Fixed** — imports `PROJECT_ROOT` |

### 11.2 Application

| # | Issue | Status |
|---|---|---|
| 9 | The ML recommendation router import was commented out; the DB router was imported under the same name, so `/api/v1/recommendation/*` never existed | **Fixed** — both routers imported explicitly and mounted at distinct prefixes |
| 10 | The DB recommendation router was mounted twice | **Fixed** — single mount at `/api/v1/recommendations` |
| 11 | `SecurityConfig` fell back to a placeholder secret | **Fixed** — explicit `_DEV_FALLBACK_SECRET`; production rejects placeholders, short values and `CHANGE_ME` |
| 12 | `load_dotenv(override=True)` let a committed `.env` silently reset `ENVIRONMENT`, defeating every production safeguard | **Fixed** — `override=False`; real env vars always win |
| 13 | `.env` / `.env.docker` contained committed credentials | **Mitigated** — `.env.example` added with `CHANGE_ME` placeholders and a generation hint; `.gitignore` now excludes `.env*`. **Secrets remain in git history — rotate them manually.** |
| 14 | `auth/routes.py` referenced an undefined `response` after a `return` | **Fixed** — unreachable dead code removed |
| 15 | `main.py` defined the `"health"` dict key twice; the second silently overwrote the first | **Fixed** — renamed to `health_check` |
| 16 | `from ctypes import Union` shadowed `typing.Union` in 4 ORM models | **Fixed** — bogus imports removed |
| 17 | `prometheus_client.Enum` and `enum.Enum` shadowed each other in `recommendation_metrics.py`, breaking monitoring init | **Fixed** — only stdlib `Enum` imported |
| 18 | Duplicate `create_auth_response` / `AccountStatus` definitions shadowed their imports | **Fixed** |
| 19 | Duplicate index on `user_profiles.reading_personality` caused `index ... already exists` on schema creation | **Fixed** — redundant `Index()` removed |
| 20 | The root endpoint returned the product name where the API name was expected | **Fixed** — returns `f"{APP_NAME} API"` |

### 11.3 Frontend

| # | Issue | Status |
|---|---|---|
| 21 | `store/` and `providers/` directories empty; `axios` declared but unused | **Partially fixed** — `axios` and `@types/axios` removed. `store/` and `providers/` left in place (empty dirs are untracked by git) |
| 22 | Refresh token stored but never used; no 401 auto-refresh | **Fixed** — `client.ts` refreshes on 401 and retries once, collapsing concurrent 401s into a single refresh |
| 23 | `(auth)` layout linked to `/privacy`, `/terms`, `/about`, which had no pages | **Fixed** — all three pages created |
| 24 | `lib/api/auth.ts` used divergent localStorage keys (`access_token` vs `auth_token`) | **Fixed** — delegates to the shared `tokenStorage` |

### 11.4 Infrastructure & tooling

| # | Issue | Status |
|---|---|---|
| 25 | `.gitignore` was UTF-16 with concatenated entries (`reports/apps/api/ml/artifacts/*`) | **Fixed** — clean UTF-8, ignores `.env*`, `data/`, ML artifacts, `node_modules` |
| 26 | `.pre-commit-config.yaml` was malformed YAML (`*` where `-` belongs) | **Fixed** — valid; ruff, black, pre-commit-hooks |
| 27 | Two conflicting `pytest.ini` files; the API one had invalid options | **Fixed** — root `pytest.ini` is authoritative; `apps/api/pytest.ini` deleted |
| 28 | No root `Dockerfile`, yet workflow path filters referenced one | **Fixed** — thin alias added |
| 29 | `api.yml` build context `../..` escaped the repository | **Fixed** — context is `.` |
| 30 | Frontend `Dockerfile` lacked a `\` continuation between `addgroup` and `adduser` | **Fixed** — image build succeeds |
| 31 | Python version drift: Docker 3.11, `ci.yml` 3.12, black target `py312` | **Fixed** — all pinned to 3.11 |
| 32 | `api.yml` ran `pytest tests/api/`, which does not exist | **Fixed** — runs `pytest` against `apps/api/tests/` |
| 33 | black config `target-version = "py312"` was a string, not a list — every invocation failed | **Fixed** — `["py311"]` |
| 34 | Prometheus config self-documented a path it did not occupy; the prod compose referenced `prometheus.prod.yml`, which did not exist | **Fixed** — `infrastructure/compose/prometheus.prod.yml` created; header corrected; false Redis/Postgres scrape jobs removed |
| 35 | API container had no healthcheck and ran as root; missing `libpq5`/`libgomp1` | **Fixed** — non-root `appuser`, healthcheck on `/api/v1/health/liveness`, required shared libraries installed |
| 36 | Only the API and frontend were exposed in prod; no TLS-terminating proxy | **Fixed** — `docker-compose.prod.yml` publishes only nginx; `/api/`, `/grafana/`, docs and metrics routed |
| 37 | `ml/paths.py` used `parents[3]`, which **raises `IndexError` inside the container** (`/app/ml/paths.py` has only 3 ancestors) and derived `ARTIFACT_DIR` from the repo root rather than the module, so it pointed outside the mounted `/app/ml/artifacts` volume | **Fixed** — layout-aware resolution; artifacts/models derive from the module location. Verified in both repo and simulated container layouts |
| 38 | Prod compose frontend `dockerfile: ../../infrastructure/...` was resolved relative to the *context* (`apps/frontend/web`), yielding the non-existent `apps/infrastructure/docker/frontend/Dockerfile` | **Fixed** — `../../../infrastructure/docker/frontend/Dockerfile` |
| 39 | Dev compose `ml-train` referenced `infrastructure/docker/ml/Dockerfile`, which does not exist | **Fixed** — reuses the API image, which already contains the full ML stack |
| 40 | Dev compose mounted `./prometheus.yml`, which does not exist in `infrastructure/compose/` | **Fixed** — points at `../docker/api/prometheus.yml` |
| 41 | Prometheus scrape jobs targeted `redis:6379` and `postgres:5432`, neither of which exposes a Prometheus endpoint | **Fixed** — false jobs removed; exporters documented |
| 42 | `POST /admin/reload` and `GET /admin/registry` were documented "admin only" but performed **no authentication**; nginx also routed `/admin/*` to the frontend, so the routes were unreachable *and* unprotected | **Fixed** — `X-Admin-Key` guard (`ADMIN_API_KEY`), constant-time comparison, disabled in staging/production when unset; nginx now routes `/admin/*` and `/monitor/*` to the API. Verified across 7 environment/key combinations |

### 11.5 Documentation

`docs/DEPLOYMENT_GUIDE.md` is now a complete deployment runbook (server prep, secret
generation, model-artifact pipeline, TLS, backups, updates, monitoring, troubleshooting).

The following remain **stubs**: `docs/METRICS.md`, `docs/PROJECT_STATUS.md`,
`docs/SUCCESS_METRICS.md`, `docs/RELEASE_CHECKLIST.md`, `docs/DECISION_002.md`,
`docs/technical_decisions.md`, `docs/RISKS.md`, `docs/v2.md`. `docs/millstone.md`,
`docs/elevator_pitch.md`, `docs/phase_3c_content_recommendation.md` and `docs/datasets.md`
are substantive.

> The README references `docs/assets/logo.png`, which does not exist, and its code blocks
> describe a `ml/` layout differing from the actual `apps/api/ml/`.

### 11.6 Deliberate non-goals

- **`api` runs with `--workers 1`.** The FAISS index and ALS model are ~750 MB of
  in-process state; multiple workers would multiply that. Scale vertically or add replica
  containers behind nginx instead.
- **Black is informational in CI.** The repository was never black-formatted; gating on it
  would fail ~100 pre-existing files and block unrelated changes. Correctness is gated by
  ruff.
- **`E712` is not linted.** Ruff rewrites `Model.col == False` to `not Model.col`, which is
  **wrong** for SQLAlchemy filter expressions. Enabling it would invite a bug.

---

## 12. Setup & Running Locally

### 12.1 Prerequisites

Python 3.11+ · Node.js 20+ · PostgreSQL 16 (or Docker) · Redis 7 (or Docker).

### 12.2 Backend

```bash
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Linux / macOS

pip install -r requirements.txt
```

Create `.env` at the repository root (copied from the existing `.env`, with real secrets):

```env
DATABASE_URL=postgresql://postgres:<password>@localhost:5432/book_recommendation_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=<long-random-string>
JWT_SECRET=<long-random-string>
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Run the API:

```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

| URL | Purpose |
|---|---|
| http://localhost:8000 | Root info |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/health | Health check |
| http://localhost:8000/metrics | Prometheus metrics |

Apply migrations with `alembic upgrade head`.

### 12.3 Frontend

```bash
cd apps/frontend/web
npm install
npm run dev        # http://localhost:3000
```

Scripts: `dev`, `build`, `start`, `lint`. The client reads `NEXT_PUBLIC_API_URL`
(`.env.local` currently sets `http://localhost:8000/api/v1`; the code fallback is `127.0.0.1`).

### 12.4 Full stack with Docker

```bash
docker compose -f infrastructure/compose/docker-compose.dev.yml --profile monitoring up -d
```

| Service | Port | Profile |
|---|---|---|
| `frontend` | 3000 | default |
| `api` | 8000 | default |
| `postgres` | 5432 | default |
| `redis` | 6379 | default |
| `pgadmin` | 5050 | `dev`, `tools` |
| `prometheus` | 9090 | `monitoring`, `dev` |
| `grafana` | 3000 | `monitoring`, `grafana`, `dev` |
| `node-exporter` | 9100 | `monitoring`, `dev` |
| `cadvisor` | 8080 | `monitoring`, `dev` |
| `ml-train` | — | `ml`, `training` |

Persistent volumes: `book_postgres_data`, `book_redis_data`, `book_pgadmin_data`,
`book_ml_artifacts`, `book_ml_models`, `book_data_processed`, `book_logs`,
`book_prometheus_data`, `book_grafana_data`. Network: `book_network` (bridge).

> `docker-compose.yml` at the repository root is **empty (0 bytes)** — use the file under
> `infrastructure/compose/`.

---

## 13. Testing

The suite lives in `apps/api/tests/`: `conftest.py`, `test_client.py`, `test_health.py`,
`test_author_api.py`, `test_recommendation_api.py`, `test_async_example.py`.

Module-level tests also exist alongside ML code: `ml/popularity/test_popularity.py`,
`ml/content/test_content.py`, `ml/content/test_content_service.py`,
`ml/collaborative/test_collaborative.py`, `ml/hybrid/test_hybrid.py`,
`ml/evaluation/test_evaluator.py`, `ml/retrieval/test_retriever.py`.

Markers defined in `apps/api/pytest.ini`: `unit`, `integration`, `slow`, `health`, `api`.

```bash
pytest                                          # root config → apps/api/tests
pytest --cov=apps/api --cov-report=term-missing # with coverage
```

> Because two `pytest.ini` files exist with different settings, run tests from a consistent working
> directory (see §11 #16).

---

## 14. Deployment & Infrastructure

**API image** (`infrastructure/docker/api/Dockerfile`) — `python:3.11-slim`, installs `gcc`, `g++`, `curl`,
pip-installs `requirements.txt`, copies `apps/api` to `/app`, creates `ml/artifacts`, `ml/models`, `logs`,
exposes 8000, runs Uvicorn.

**Frontend image** (`infrastructure/docker/frontend/Dockerfile`) — three-stage `node:22-alpine` build:
`deps` (npm ci) → `builder` (next build, standalone output) → `runner` (non-root `nextjs` uid 1001, copies
`public`, `.next/standalone`, `.next/static`; exposes 3000; `node server.js`). *This file currently has a
syntax defect — see §11 #20.*

**CI/CD** — `.github/workflows/ci.yml` runs black/ruff/pytest on push to `main`/`develop` and PRs to
`develop`. `.github/workflows/api.yml` provisions a throwaway PostgreSQL service, runs the test suite with
coverage, builds and pushes a Docker image to Docker Hub, then runs a `deploy` job that only echoes the
version. **No real deployment target is wired up.**

**Target platforms named in the docs:** Render, Railway, AWS. `docs/DEPLOYMENT_GUIDE.md` is a stub, so a
functional deployment guide still needs to be written.

---

## 15. Observability

**Metrics** (`app/services/recommendation_metrics.py`) — Prometheus client instruments:

| Type | Metric |
|---|---|
| Counter | `recommendations_generated_total{type,status}` |
| Counter | `recommendation_requests_total{endpoint,method}` |
| Counter | `recommendation_errors_total{endpoint,error_type}` |
| Counter | `cache_operations_total{operation,result}` |
| Histogram | `recommendation_duration_seconds{type}` |
| Histogram | `request_duration_seconds{endpoint,method}` |
| Histogram | `recommendation_count_per_request{type}` |
| Gauge | service status |

Exposed at `/metrics` in Prometheus text format.

**Monitoring** — `MonitoringService` logs requests and recommendations and flushes structured logs on
shutdown; `RecommendationMonitor` maintains rolling latency/error statistics with alert thresholds, surfaced
through `/monitor/metrics`, `/monitor/summary`, `/monitor/alerts`.

**Health** — `/health` (composite), `/api/v1/health/liveness`, `/api/v1/health/readiness`,
`/api/v1/health/details`, `/api/v1/health/ml-services`. The database probe runs `SELECT 1`; the Redis probe
runs `PING`; the ML probe queries the service registry and reports `healthy` or `degraded`.

**Alerting stack** — Prometheus scrapes `api:8000/metrics`, `localhost:9090`, `redis:6379`, and
`postgres:5432` every 15 s. Grafana is provisioned with the Prometheus datasource and dashboard provider.
Alertmanager and rule files are present but commented out.

---

## 16. Glossary

| Term | Meaning |
|---|---|
| **ALS** | Alternating Least Squares — matrix-factorisation algorithm used for implicit-feedback collaborative filtering |
| **Artifact** | A serialized model/index/parquet file produced offline and loaded by the API at runtime |
| **Cold start** | A user or item with little or no interaction history; handled here by the popularity fallback |
| **Content-based** | Recommending items whose descriptive text is semantically similar to what the user liked |
| **Collaborative filtering** | Recommending based on the behaviour of users with similar taste |
| **Embedding** | A dense 384-dimension vector representing a book's text via `all-MiniLM-L6-v2` |
| **FAISS** | Facebook AI Similarity Search — the library providing the vector index |
| **Hybrid** | Fusion of multiple recommendation signals into a single ranked score |
| **IndexFlatIP** | A FAISS index doing exact inner-product search; equivalent to cosine on normalised vectors |
| **Lifespan** | FastAPI's modern startup/shutdown context manager, replacing `on_event` |
| **Modular monolith** | One deployable application internally partitioned into extractable modules |
| **NDCG@K** | Normalized Discounted Cumulative Gain — rank-aware ranking quality metric |
| **Orphan rating** | A rating whose ISBN does not exist in the book catalog |
| **Popularity fallback** | Returning popularity-ranked books when personalization is impossible |
| **Registry** | `MLServiceRegistry` — the lazy-loading singleton holding the ML services |
| **Sparsity** | The proportion of empty cells in the user × item rating matrix |
| **Standalone output** | Next.js build mode emitting a self-contained server bundle for Docker |
| **Token storage** | The `localStorage`-backed singleton holding access/refresh tokens in the browser |

---

*Generated from direct inspection of the working tree. Where the README, `structure.txt`, and the code
disagree, this document follows the code and records the discrepancy in §11.*
