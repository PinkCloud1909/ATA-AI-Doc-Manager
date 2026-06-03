# DMS Backend Foundation

Minimal FastAPI backend skeleton for a document management system. This version implements only the platform foundation: app bootstrap, PostgreSQL integration, Alembic, SQLAlchemy 2.0 models, JWT auth, RBAC foundation, MinIO adapter, seed data, Docker support, and basic tests.

## Directory tree

```text
.
|-- .env.example
|-- .gitignore
|-- Dockerfile
|-- README.md
|-- alembic.ini
|-- docker-compose.yml
|-- pyproject.toml
|-- app
|   |-- __init__.py
|   |-- main.py
|   |-- alembic
|   |   |-- env.py
|   |   |-- script.py.mako
|   |   `-- versions
|   |       `-- 20260420_0001_initial_schema.py
|   |-- core
|   |   |-- __init__.py
|   |   |-- config.py
|   |   |-- db.py
|   |   |-- dependencies.py
|   |   |-- exceptions.py
|   |   |-- logging.py
|   |   `-- security.py
|   |-- modules
|   |   |-- __init__.py
|   |   |-- model_registry.py
|   |   |-- documents
|   |   |   |-- __init__.py
|   |   |   |-- domain
|   |   |   |   |-- __init__.py
|   |   |   |   `-- models.py
|   |   |   `-- infrastructure
|   |   |       |-- __init__.py
|   |   |       `-- minio_adapter.py
|   |   |-- iam
|   |   |   |-- __init__.py
|   |   |   |-- api
|   |   |   |   |-- __init__.py
|   |   |   |   |-- router.py
|   |   |   |   `-- schemas.py
|   |   |   |-- application
|   |   |   |   |-- __init__.py
|   |   |   |   |-- seed.py
|   |   |   |   `-- services.py
|   |   |   |-- domain
|   |   |   |   |-- __init__.py
|   |   |   |   |-- models.py
|   |   |   |   `-- principal.py
|   |   |   `-- infrastructure
|   |   |       |-- __init__.py
|   |   |       `-- repositories.py
|   |   |-- qa
|   |   |   |-- __init__.py
|   |   |   |-- domain
|   |   |   |   |-- __init__.py
|   |   |   |   `-- placeholder.py
|   |   |   `-- infrastructure
|   |   |       |-- __init__.py
|   |   |       `-- placeholder.py
|   |   |-- reviews
|   |   |   |-- __init__.py
|   |   |   |-- domain
|   |   |   |   |-- __init__.py
|   |   |   |   `-- models.py
|   |   |   `-- infrastructure
|   |   |       |-- __init__.py
|   |   |       `-- placeholder.py
|   |   `-- vectorization
|   |       |-- __init__.py
|   |       |-- domain
|   |       |   |-- __init__.py
|   |       |   `-- placeholder.py
|   |       `-- infrastructure
|   |           |-- __init__.py
|   |           `-- placeholder.py
|   |-- shared
|   |   |-- __init__.py
|   |   |-- enums.py
|   |   |-- schemas.py
|   |   `-- utils.py
|   `-- tests
|       |-- __init__.py
|       |-- conftest.py
|       |-- integration
|       |   |-- __init__.py
|       |   |-- test_auth.py
|       |   `-- test_system.py
|       `-- unit
|           |-- __init__.py
|           `-- test_security.py
`-- scripts
    `-- seed.py
```

## What is included

- `GET /health`
- `GET /ready`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- PostgreSQL-ready Alembic migration for the required tables and enums
- RBAC foundation using `roles`, `privileges`, `users`, and `user_roles`
- MinIO adapter foundation for stable object references such as `minio://documents/path/to/object.pdf`

No business APIs for documents, reviews, vectorization, or QA are implemented in this version.

## Local run with Docker Compose

1. Copy the environment file.

```bash
cp .env.example .env
```

2. Start the stack.

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## Local run without Docker

1. Create a Python 3.11 environment and install dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

2. Update `.env` so `DATABASE_URL` and `MINIO_ENDPOINT` point to your local services.

3. Run migrations and seed data.

```bash
alembic upgrade head
python scripts/seed.py
```

4. Start the API.

```bash
uvicorn app.main:app --reload
```

## Migrations

Apply migrations:

```bash
alembic upgrade head
```

Create a new migration later:

```bash
alembic revision -m "describe change"
```

## Seed data

Run:

```bash
python scripts/seed.py
```

Default credentials:

- Username: `admin`
- Password: `admin123`

## Testing

Install dev dependencies and run:

```bash
pytest
```

The test suite uses SQLite in memory for fast endpoint checks while the application runtime and migration path remain PostgreSQL-first.

## Endpoint checks

Health:

```bash
curl http://localhost:8000/health
```

Ready:

```bash
curl http://localhost:8000/ready
```

Login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Register:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"newuser123"}'
```

Current user:

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

MinIO:

- API endpoint: `http://localhost:9000`
- Console: `http://localhost:9001`
- Bucket: `documents`
