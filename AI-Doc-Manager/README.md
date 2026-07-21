# AI-Doc-Manager

AI document management platform with document upload/versioning, chat and voice chat, runbook generation, document scoring, and approval workflow.

<<<<<<< Updated upstream
## Project Structure

```text
AI-Doc-Manager/
  backend/          FastAPI backend, SQLAlchemy models, Alembic migrations, tests
  frontend/         Next.js frontend application
  docs/             Architecture, API, setup, and testing guides
  docker-compose.yml
=======
Current status:

- The backend can be run with Docker Compose from `backend/`.
- PostgreSQL and MinIO are included in the backend Docker Compose stack.
- The Next.js frontend in `frontend/` builds as a production standalone application.

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

From this directory:

```powershell
cd backend
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
password: Admin123!
>>>>>>> Stashed changes
```

Runtime artifacts such as local SQLite DB files, generated storage files, logs, caches, and build outputs are intentionally ignored.

## Local Backend

```powershell
cd C:\Users\ADMIN\Desktop\TKTL\AI-Doc-Manager\backend
.venv\Scripts\Activate.ps1
python setup_db.py
python scripts\seed.py
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend docs: http://localhost:8000/docs

Default login:

```text
admin / admin123
```

## Local Frontend

```powershell
cd C:\Users\ADMIN\Desktop\TKTL\AI-Doc-Manager\frontend
npm install
npm run dev
```

<<<<<<< Updated upstream
Frontend: http://localhost:3000

## Docker
=======
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

## IAM And Document Review Features

The application supports effective permission inspection for users and roles,
self-service password changes, administrator password resets, document review
scores/comments, inline preview, and forced file downloads. Password-writing
flows enforce 8-128 characters with uppercase, lowercase, numeric, special
characters, and no whitespace.

After updating an existing environment, apply migrations and re-run the
idempotent IAM seed so the new change-password, reset-password, review, and RAG
status permissions are attached to the built-in roles:

```powershell
cd backend
alembic upgrade head
python scripts/seed.py
```

## Root Compose File

To start the complete local stack from this directory:
>>>>>>> Stashed changes

```powershell
cd C:\Users\ADMIN\Desktop\TKTL\AI-Doc-Manager
docker compose up --build
```

<<<<<<< Updated upstream
## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [API Endpoints](docs/API_ENDPOINTS.md)
- [Run Guide](docs/RUN_GUIDE.md)
- [Quick Setup](docs/QUICK_SETUP.md)
- [Frontend/Backend Guide](docs/FRONTEND_BACKEND_GUIDE.md)
- [Test API Guide](docs/TEST_API_GUIDE.md)
=======
For backend-only development, run Docker Compose from:

```text
backend/
```

## Run The Backend Without Docker

Use this only if you already have PostgreSQL and MinIO running locally.

From `backend/`:

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
>>>>>>> Stashed changes
