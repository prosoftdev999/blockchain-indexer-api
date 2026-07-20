# Blockchain Indexer API

[![Tests](https://github.com/prosoftdev999/blockchain-indexer-api/actions/workflows/tests.yml/badge.svg)](https://github.com/prosoftdev999/blockchain-indexer-api/actions/workflows/tests.yml)

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

A production-ready blockchain indexer built with **FastAPI**, **PostgreSQL**, **Redis**, **Celery**, and **Web3.py**.

The application continuously synchronizes confirmed Ethereum Sepolia blocks and transactions into PostgreSQL while exposing a REST API for querying indexed blockchain data.

---

# Features

- Ethereum Sepolia blockchain indexing
- Automatic background synchronization
- FastAPI REST API
- PostgreSQL database
- Redis message broker
- Celery Worker
- Celery Beat scheduler
- Docker Compose deployment
- SQLAlchemy 2.0 ORM
- Alembic migrations
- Pydantic Settings
- GitHub Actions CI
- Pytest test suite
- OpenAPI / Swagger UI

---

# Technology Stack

| Technology | Version |
|------------|---------|
| Python | 3.12 |
| FastAPI | Latest |
| SQLAlchemy | 2.x |
| PostgreSQL | 17 |
| Redis | 7 |
| Celery | 5.x |
| Docker | Latest |
| Docker Compose | Latest |
| Web3.py | Latest |
| Pytest | Latest |

---

# Project Structure

```
blockchain-indexer-api
│
├── app
│   ├── api
│   ├── core
│   ├── crud
│   ├── db
│   ├── models
│   ├── schemas
│   ├── services
│   └── workers
│
├── migrations
├── tests
├── .github/workflows
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
└── LICENSE
```

---

# Architecture

```
Ethereum Sepolia RPC
        │
        ▼
 Celery Beat Scheduler
        │
        ▼
 Celery Worker
        │
        ▼
Web3.py Block Fetcher
        │
        ▼
 PostgreSQL Database
        │
        ▼
 FastAPI REST API
        │
        ▼
 API Clients
```

---

# Environment Variables

Create a `.env` file.

```env
APP_NAME=Blockchain Indexer API
APP_VERSION=1.0.0
DEBUG=true

DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/blockchain_indexer

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

BLOCKCHAIN_RPC_URL=https://ethereum-sepolia-rpc.publicnode.com
BLOCKCHAIN_CHAIN_ID=11155111

START_BLOCK=0
CONFIRMATION_BLOCKS=12
INDEXER_BATCH_SIZE=10

SYNC_BATCH_SIZE=5
SYNC_INTERVAL_SECONDS=30
```

---

# Running with Docker

Build containers

```bash
docker compose build
```

Start services

```bash
docker compose up -d
```

Check status

```bash
docker compose ps
```

View logs

```bash
docker compose logs -f
```

Stop

```bash
docker compose down
```

---

# API Documentation

Swagger UI

```
http://localhost:8000/docs
```

OpenAPI

```
http://localhost:8000/openapi.json
```

---

# API Endpoints

## Health

```
GET /health
```

---

## Indexer Status

```
GET /api/v1/indexer/status
```

Example Response

```json
{
  "chain_id": 11155111,
  "blockchain_head": 11309735,
  "latest_confirmed_block": 11309723,
  "latest_indexed_block": 11309209,
  "confirmation_blocks": 12,
  "status": "idle"
}
```

---

## Blocks

```
GET /api/v1/blocks
```

```
GET /api/v1/blocks/{number}
```

---

## Transactions

```
GET /api/v1/transactions
```

Example

```
GET /api/v1/transactions?limit=10
```

---

# Background Synchronization

The indexer automatically:

- Reads blockchain head
- Waits for confirmations
- Downloads confirmed blocks
- Downloads transactions
- Saves data into PostgreSQL
- Updates synchronization state

Synchronization is executed by Celery Worker.

Scheduling is handled by Celery Beat.

---

# Database

Tables

- blocks
- transactions
- indexer_states

Relationships

```
Block
 └── Transactions
```

---

# Running Tests

```
python -m pytest -v
```

Current Status

```
11 passed
```

---

# GitHub Actions

The project includes automated CI.

Workflow

```
.github/workflows/tests.yml
```

The workflow automatically

- Installs Python
- Installs dependencies
- Runs Pytest
- Reports results

---

# Docker Services

| Service | Description |
|----------|-------------|
| api | FastAPI server |
| worker | Celery Worker |
| beat | Celery Beat Scheduler |
| postgres | PostgreSQL Database |
| redis | Redis |

---

# Example Docker Commands

Start

```bash
docker compose up -d
```

Restart

```bash
docker compose restart
```

Logs

```bash
docker compose logs -f api
```

Worker Logs

```bash
docker compose logs -f worker
```

Beat Logs

```bash
docker compose logs -f beat
```

Stop

```bash
docker compose down
```

---

# Security

- Environment variables
- Docker isolation
- SQLAlchemy ORM
- Async PostgreSQL driver
- Parameterized SQL queries

---

# Future Improvements

- WebSocket event streaming
- Multi-chain indexing
- Address balance API
- ERC20 token transfers
- NFT indexing
- Prometheus metrics
- Grafana dashboards
- Kubernetes deployment

---

# License

MIT License

---

# Author

**Johan Bergman**

GitHub

https://github.com/prosoftdev999

---

# Project Status

- Dockerized
- Tested
- GitHub Actions Enabled
- Ethereum Sepolia Indexing
- Production Ready