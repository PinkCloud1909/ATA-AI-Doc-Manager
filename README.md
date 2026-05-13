# AI-Doc-Manager

This repository contains the project source inside the `AI-Doc-Manager/` directory.

Current status:

- The backend can be run with Docker Compose from `AI-Doc-Manager/backend/`.
- PostgreSQL and MinIO are included in the backend Docker Compose stack.
- The frontend in `AI-Doc-Manager/frontend/` is currently incomplete on `master`, so the root Docker Compose stack should not be used yet.

## Prerequisites

- Docker Desktop
- Docker Compose
- Python 3.11, only if you want to run the backend without Docker

Before starting the project, make sure Docker Desktop is running:

```powershell
docker ps
```

If this command returns a Docker engine connection error, open Docker Desktop and wait until it is ready.

## Run The Backend

From the repository root:

```powershell
cd AI-Doc-Manager/backend
```

Create the local environment file if it does not exist:

```powershell
Copy-Item .env.example .env
```

On macOS or Linux:

```bash
cp .env.example .env
```

Build and start the backend stack:

```powershell
docker compose up -d --build
```

The `api` container automatically runs database migrations and seed data on startup.

## Service URLs

- Backend API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- PostgreSQL: localhost:5432
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001

Default admin account:

```text
username: admin
password: admin123
```

## Common Commands

Run these commands from `AI-Doc-Manager/backend/`.

Check containers:

```powershell
docker compose ps
```

View backend logs:

```powershell
docker compose logs -f api
```

Run migrations manually:

```powershell
docker compose exec api alembic upgrade head
```

Run seed data manually:

```powershell
docker compose exec api python scripts/seed.py
```

Stop containers:

```powershell
docker compose down
```

Stop containers and remove database/MinIO volumes:

```powershell
docker compose down -v
```

## Important Note About The Root Compose File

Do not run this from `AI-Doc-Manager/` on `master` yet:

```powershell
docker compose up --build
```

The root Compose file includes the frontend service, but the frontend on `master` is not ready to build yet.

For backend-only development, always run Docker Compose from:

```text
AI-Doc-Manager/backend/
```

## Run The Backend Without Docker

Use this only if you already have PostgreSQL and MinIO running locally.

From `AI-Doc-Manager/backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

On macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://localhost:8000
```
