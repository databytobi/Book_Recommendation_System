# 📚 Hybrid Book Recommendation System

<p align="center">
  <img src="docs/assets/logo.png" alt="Book Recommendation System Logo" width="180"/>
</p>

<p align="center">
A scalable, production-ready hybrid recommendation engine designed to power modern book discovery platforms through machine learning, semantic search, and personalized recommendations.
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791)
![Redis](https://img.shields.io/badge/Redis-Cache-red)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-orange)
![Docker](https://img.shields.io/badge/Docker-Containerization-blue)
![License](https://img.shields.io/badge/License-MIT-green)

</p>

---

# Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Project Goals](#project-goals)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Next Steps](#next-steps)

---

# Overview

The **Hybrid Book Recommendation System** is a production-grade recommendation engine that helps users discover books tailored to their interests, reading history, and preferences.

Instead of relying solely on keyword searches, the platform combines multiple recommendation strategies—including popularity-based, content-based, collaborative filtering, and semantic similarity—to deliver accurate, diverse, and personalized recommendations.

The project is designed with scalability and maintainability in mind, making it suitable for deployment as the recommendation backbone of a modern online book platform.

---

# Problem Statement

Modern online bookstores contain millions of books spanning countless genres, authors, languages, and themes. While this abundance provides users with many choices, it also introduces a significant challenge:

> **Information Overload**

Traditional search systems require users to know exactly what they are looking for, making it difficult to discover new books that align with their interests.

This project addresses that challenge by building a hybrid recommendation engine capable of:

- Delivering personalized recommendations
- Supporting both new and returning users
- Handling large-scale datasets efficiently
- Reducing cold-start problems
- Improving recommendation diversity
- Providing real-time recommendations
- Integrating seamlessly with modern web applications

---

# Project Goals

## Primary Goals

- Build a scalable recommendation engine
- Deliver personalized recommendations
- Combine multiple recommendation algorithms
- Design a production-ready backend
- Provide REST APIs for frontend applications
- Support future scalability

## Secondary Goals

- Semantic book discovery
- Explainable recommendations
- Real-time personalization
- AI-powered recommendation capabilities
- Continuous model improvements
- Cloud-native deployment

---

# Key Features

## Recommendation Engine

- Popularity-Based Recommendation
- Content-Based Filtering
- Collaborative Filtering
- Hybrid Recommendation Engine
- Semantic Recommendation System

---

## Personalized User Experience

- User Profiles
- Reading History
- Ratings & Reviews
- Favorite Books
- Wishlists
- Personalized Home Feed

---

## Search Features

- Keyword Search
- Author Search
- Genre Search
- Semantic Search
- Similar Books
- Natural Language Queries

---

## Machine Learning

- TF-IDF Vectorization
- Cosine Similarity
- Matrix Factorization
- Singular Value Decomposition (SVD)
- Sentence Transformers
- Hybrid Ranking Strategy

---

## Backend Features

- RESTful APIs
- Authentication
- API Versioning
- Background Jobs
- Recommendation Caching
- Logging & Monitoring

---

## Infrastructure

- Dockerized Services
- CI/CD Pipelines
- Modular Architecture
- Production Deployment
- Redis Caching
- Vector Search

---

# Technology Stack

## Backend

- FastAPI
- Python 3.12+

## Machine Learning

- Scikit-learn
- Surprise
- Implicit
- Sentence Transformers

## Database

- PostgreSQL

## Cache

- Redis

## Vector Database

- FAISS (or ChromaDB)

## Frontend

- Next.js

## DevOps

- Docker
- Docker Compose
- GitHub Actions

## Deployment

- Render
- Railway
- AWS

---

# System Architecture

The application follows a **Modular Monolith Architecture** designed for future evolution into microservices.

```
                 +-----------------------+
                 |     Next.js Frontend  |
                 +-----------+-----------+
                             |
                             |
                  REST API Requests
                             |
                             ▼
                 +-----------------------+
                 |    FastAPI Backend    |
                 +-----------+-----------+
                             |
        +----------+---------+---------+----------+
        |          |                   |          |
        ▼          ▼                   ▼          ▼
 Recommendation   Search          User/Auth   Analytics
     Module       Module           Module      Module
        |
        ▼
 Recommendation Orchestrator
        |
        +-----------------------------+
        |             |               |
        ▼             ▼               ▼
 Popularity     Content-Based   Collaborative
   Engine          Engine          Engine
        \             |             /
         \            |            /
          +-----------+-----------+
                      |
               Hybrid Ranker
                      |
                      ▼
           Final Book Recommendations
```

A detailed architecture document with sequence diagrams, deployment diagrams, and ML pipelines is available in the `/docs/architecture` directory.

---

# Repository Structure

```text
book-recommendation-system/

├── apps/
│   ├── api/
│   ├── frontend/
│   └── worker/
│
├── ml/
│   ├── preprocessing/
│   ├── recommenders/
│   │   ├── popularity/
│   │   ├── content_based/
│   │   ├── collaborative/
│   │   └── hybrid/
│   ├── training/
│   ├── evaluation/
│   └── models/
│
├── infrastructure/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── deployment/
│   └── ml/
│
├── tests/
│
├── scripts/
│
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

# Installation

## Clone the Repository

```bash
git clone https://github.com/yourusername/book-recommendation-system.git

cd book-recommendation-system
```

---

## Create a Virtual Environment

```bash
python -m venv .venv
```

### Activate

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file.

```env
DATABASE_URL=
REDIS_URL=
SECRET_KEY=
JWT_SECRET=
VECTOR_DB_PATH=
```

---

## Start Docker Services

```bash
docker compose up -d
```

---

# Running the Project

Start the FastAPI server

```bash
uvicorn app.main:app --reload
```

Visit

```
http://localhost:8000
```

Interactive API Documentation

```
http://localhost:8000/docs
```

ReDoc Documentation

```
http://localhost:8000/redoc
```

---

# Next Steps

The next section of this README covers:

- API Documentation
- Recommendation Algorithms
- Machine Learning Pipeline
- Screenshots
- Roadmap
- Future Enhancements
- Contributing
- License
- Contact