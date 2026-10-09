# 🏗️ System Architecture

## Overview

The Hybrid Book Recommendation System is designed using a **modular monolithic architecture**, allowing independent development of features while maintaining a single deployable application.

As the platform grows, individual modules can be extracted into independent microservices with minimal refactoring.

---

# High-Level Architecture

```mermaid
flowchart LR

User((User))

Frontend[Next.js Frontend]

Gateway[FastAPI Backend]

Auth[Authentication Module]

Search[Search Module]

Users[User Service]

Recommendation[Recommendation Service]

Database[(PostgreSQL)]

Redis[(Redis Cache)]

Vector[(FAISS / ChromaDB)]

User --> Frontend

Frontend --> Gateway

Gateway --> Auth

Gateway --> Users

Gateway --> Search

Gateway --> Recommendation

Auth --> Database

Users --> Database

Search --> Database

Recommendation --> Database

Recommendation --> Redis

Recommendation --> Vector
```

---

# Layered Architecture

```
Presentation Layer
──────────────────────────

Next.js Frontend
Mobile App (Future)

        │

Application Layer
──────────────────────────

REST API
Authentication
Business Logic
Recommendation API

        │

Recommendation Layer
──────────────────────────

Popularity Engine

Content-Based Engine

Collaborative Filtering

Hybrid Ranker

Semantic Search

        │

Data Layer
──────────────────────────

PostgreSQL

Redis

Vector Database

Model Files
```

---

# Recommendation Pipeline

```mermaid
flowchart TD

User --> Login

Login --> RequestRecommendation

RequestRecommendation --> RecommendationService

RecommendationService --> Popularity

RecommendationService --> ContentBased

RecommendationService --> Collaborative

Popularity --> Hybrid

ContentBased --> Hybrid

Collaborative --> Hybrid

Hybrid --> Ranking

Ranking --> TopBooks

TopBooks --> API

API --> Frontend

Frontend --> User
```

---

# Content-Based Recommendation Flow

```mermaid
flowchart LR

Books --> Metadata

Metadata --> Cleaning

Cleaning --> TFIDF

TFIDF --> CosineSimilarity

CosineSimilarity --> SimilarBooks

SimilarBooks --> API
```

---

# Collaborative Filtering Workflow

```mermaid
flowchart LR

Ratings --> UserItemMatrix

UserItemMatrix --> MatrixFactorization

MatrixFactorization --> LatentVectors

LatentVectors --> Predictions

Predictions --> Recommendations
```

---

# Hybrid Recommendation Strategy

```mermaid
flowchart TD

PopularityScore

ContentScore

CollaborativeScore

PopularityScore --> WeightedRank

ContentScore --> WeightedRank

CollaborativeScore --> WeightedRank

WeightedRank --> DiversityFilter

DiversityFilter --> FinalRecommendations
```

---

# Semantic Search Pipeline

```mermaid
flowchart LR

SearchQuery

SearchQuery --> EmbeddingModel

EmbeddingModel --> QueryVector

QueryVector --> FAISS

FAISS --> SimilarBooks

SimilarBooks --> SearchResults
```

---

# Machine Learning Pipeline

```mermaid
flowchart TD

RawDataset

RawDataset --> DataCleaning

DataCleaning --> FeatureEngineering

FeatureEngineering --> TrainValidationSplit

TrainValidationSplit --> ModelTraining

ModelTraining --> Evaluation

Evaluation --> ModelRegistry

ModelRegistry --> ProductionAPI
```

---

# Request Lifecycle

```mermaid
sequenceDiagram

participant User

participant Frontend

participant API

participant Recommendation

participant Database

participant Redis

User->>Frontend: Open Homepage

Frontend->>API: GET /recommendations

API->>Redis: Check Cache

alt Cache Hit

Redis-->>API: Cached Recommendations

else Cache Miss

API->>Recommendation: Generate Recommendations

Recommendation->>Database: Fetch User Data

Database-->>Recommendation: Reading History

Recommendation-->>API: Ranked Books

API->>Redis: Cache Results

end

API-->>Frontend: Recommendation List

Frontend-->>User: Display Books
```

---

# Database Architecture

```
Users
│
├── id
├── username
├── email
└── preferences

Books
│
├── id
├── title
├── author
├── genre
├── description
└── embedding

Ratings
│
├── user_id
├── book_id
└── rating

ReadingHistory
│
├── user_id
├── book_id
└── timestamp

Recommendations
│
├── user_id
├── book_id
└── score
```

---

# Component Responsibilities

## Frontend

- User interface
- Authentication
- Search
- Recommendation display
- Reading dashboard

---

## API Layer

- Authentication
- Request validation
- Business logic
- API documentation
- Response formatting

---

## Recommendation Service

- Recommendation orchestration
- Algorithm selection
- Score aggregation
- Result ranking

---

## Search Service

- Keyword search
- Semantic search
- Author search
- Genre filtering

---

## User Service

- User profiles
- Reading history
- Ratings
- Preferences

---

## Database

Stores

- Users
- Books
- Ratings
- Reading history
- Metadata

---

## Redis

Caches

- Popular recommendations
- User recommendations
- Frequently searched books

---

## Vector Database

Stores

- Sentence embeddings
- Book embeddings
- Semantic search vectors

---

# Deployment Architecture

```mermaid
flowchart TD

Internet

Internet --> LoadBalancer

LoadBalancer --> Frontend

LoadBalancer --> FastAPI

FastAPI --> PostgreSQL

FastAPI --> Redis

FastAPI --> VectorDB

MLPipeline --> ModelStorage

ModelStorage --> FastAPI
```

---

# Future Architecture

The current implementation follows a modular monolith. As system demand increases, individual modules can evolve into independent services.

Future extraction candidates include:

- Authentication Service
- Recommendation Service
- Search Service
- Machine Learning Service
- Notification Service

These services can communicate through REST APIs or asynchronous messaging systems such as RabbitMQ or Kafka.

---

# Architecture Principles

The system is designed around the following engineering principles:

- Separation of Concerns
- Single Responsibility
- Scalability
- Maintainability
- Testability
- Fault Isolation
- Extensibility
- Performance Optimization
- Cloud Readiness
- API-First Design