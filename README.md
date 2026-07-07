# DocuSense AI (In Progress)

DocuSense AI is a production-grade, asynchronous knowledge engine designed to ingest, parse, and query large-scale technical documentation and codebases. 

This project is being built **systematically and incrementally** from the ground up to focus heavily on clean backend architecture, asynchronous data pipelines, and advanced retrieval mechanics rather than relying on out-of-the-box AI wrappers.

## What I Am Building in This Project

* **Phase 1: High-Performance Core API** – Building a completely asynchronous backend foundation using **FastAPI** and **PostgreSQL**, incorporating secure JWT authentication and optimized relational database schemas.
* **Phase 2: Decoupled Data Pipeline** – Implementing an independent background worker layer using **Celery/ARQ** and **Redis** to handle intensive web scraping, markdown parsing, and token tracking without blocking the main application server.
* **Phase 3: Hybrid Retrieval Engine** – Implementing **Hybrid Search** inside a single database instance using PostgreSQL's native Full-Text Search combined with **`pgvector`** for semantic similarity.
* **Phase 4: Orchestration & Guardrails** – Utilizing **LangChain** for context assembly and structuring non-deterministic LLM responses into strict, predictable data models via **Pydantic**.
* **Phase 5: Real-Time Streaming** – Enabling low-latency user interfaces by streaming generated responses token-by-token using FastAPI `StreamingResponse` via Server-Sent Events (SSE).

## Tech Stack
* **Backend Framework:** FastAPI (Async Python)
* **Database:** PostgreSQL + `pgvector`
* **Task Management:** Redis + Celery / ARQ
* **AI Ecosystem:** LangChain + Pydantic
* **DevOps:** Docker & Docker Compose