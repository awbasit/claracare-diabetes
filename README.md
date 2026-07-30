# DiaWise AI

Monorepo scaffold: FastAPI backend + React (Vite) frontend, Postgres with pgvector.

This is scaffolding only — no business logic is implemented yet.

## Structure

```text
backend/    FastAPI app (SQLAlchemy 2.0 async, Alembic, JWT auth utils)
frontend/   Vite + React + TypeScript, Tailwind, shadcn/ui, react-router-dom
docker-compose.yml
```

## Prerequisites

- Docker + Docker Compose
- Node.js 20+ (for local frontend dev outside Docker)
- Python 3.11+ (for local backend dev outside Docker)

## Quick start (Docker)

1. Copy the root env file and adjust as needed:

   ```bash
   cp .env.example .env
   ```

2. Bring up Postgres (with pgvector) and the backend:

   ```bash
   docker-compose up --build
   ```

   This starts:
   - `postgres` — `pgvector/pgvector:pg16`, with the `vector` extension enabled via `docker/init-pgvector.sql`, data persisted in the `postgres_data` named volume.
   - `backend` — FastAPI app on http://localhost:8000, auto-reloading on code changes.

3. Verify the backend is up:

   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/doctor
   ```

## Database migrations (Alembic)

With the stack running:

```bash
docker-compose exec backend alembic upgrade head
```

Or locally against a running Postgres:

```bash
cd backend
alembic upgrade head
```

To create a new migration after adding/changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe the change"
```

## Backend — local dev without Docker

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements-dev.txt   # runtime deps + pytest/ruff/mypy
cp .env.example .env          # then set DATABASE_URL to a reachable Postgres
uvicorn app.main:app --reload
```

`requirements.txt` is runtime-only; `requirements-dev.txt` layers test and lint
tooling on top (mirrors the frontend's `dependencies`/`devDependencies` split).

Run tests:

```bash
pytest
```

### Linting and type-checking

```bash
ruff check .           # lint
ruff format --check .  # formatting
mypy app/               # type-check
```

Config for both lives in `backend/pyproject.toml`. From the repo root, the
same checks are also available via:

```bash
make lint          # ruff check
make format-check   # ruff format --check
make typecheck      # mypy app/
make check          # all three
make test           # pytest, via the running docker-compose backend service
```

## Frontend — local dev

```bash
cd frontend
npm install
cp .env.example .env          # set VITE_API_BASE_URL if not using the default
npm run dev
```

The dev server runs on http://localhost:5173 and talks to the backend via `VITE_API_BASE_URL` (see `src/services/api.ts`).

## Environment variables

See `.env.example` (root, for docker-compose), `backend/.env.example`, and `frontend/.env.example` for the full list of variables and their defaults.
