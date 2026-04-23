# AI-Doc-Manager Monorepo

This repository combines:

- `backend/` — FastAPI backend (merged from `atna-doc-backend`)
- `frontend/` — frontend application
- `docker-compose.yml` — root orchestration for local development

## Project Layout

```text
AI-Doc-Manager/
├─ backend/
├─ frontend/
├─ docker-compose.yml
└─ .env.example
```

## Quick Start (root)

1. Create environment file:

```bash
cp .env.example .env
```

2. Build and run all services:

```bash
docker compose up --build
```

3. Access services:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001

To stop:

```bash
docker compose down
```
inIO Console: http://localhost:9001

## Migration + seed backend

`backend` tự chạy migration + seed khi start. Chạy tay nếu cần:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed.py
```

Default admin:
- username: `admin`
- password: `admin123`

---

## Development

### Backend (FastAPI)

Located in `./backend/`:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -e .[dev]
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

Backend starts at http://localhost:8000. Docs at `/docs`.

### Frontend (Next.js)

Located in `./frontend/`:

```bash
cd frontend
npm install
npm run dev
```

Frontend starts at http://localhost:3000. API URL configured via `NEXT_PUBLIC_API_URL` env var.

### Tests

```bash
# Backend tests
cd backend && pytest tests/ -v

# Frontend tests
cd frontend && npm run test
```

---

## Structure

```
AI-Doc-Manager/
├── backend/                  # FastAPI (from atna-doc-backend)
│   ├── app/
│   │   ├── core/            # Config, DB, security, dependencies
│   │   ├── modules/         # Feature modules (IAM, documents, etc)
│   │   ├── shared/          # Shared enums, schemas, utils
│   │   └── tests/           # Unit & integration tests
│   ├── pyproject.toml       # Dependencies
│   ├── alembic.ini          # Migration config
│   ├── Dockerfile
│   └── scripts/             # Seed, utilities
├── frontend/                # Next.js
│   ├── src/
│   │   ├── app/            # App Router pages
│   │   ├── components/     # UI components
│   │   ├── lib/            # API client, utilities
│   │   ├── hooks/          # Custom hooks
│   │   ├── stores/         # Zustand state
│   │   └── types/          # TypeScript types
│   ├── package.json
│   ├── Dockerfile
│   └── next.config.ts
├── docker-compose.yml      # Orchestration
├── .env.example            # Environment template
├── .gitignore
├── .dockerignore
└── README.md               # This file
```

---

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, MinIO, JWT/RBAC
- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS, Zustand, React Query
- **Infrastructure**: Docker, Docker Compose, PostgreSQL, MinIO
- **AI**: Gemini API (integration pending)

---

## Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Backend
JWT_SECRET_KEY=<your-secret-key>
DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/dms_backend

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_BUCKET=documents
```

See `.env.example` for full list.

---

## Notes

- Do **not** commit `.env` to Git
- On production, inject secrets via Kubernetes/Docker Secrets
- Frontend API URL is resolved at runtime from `NEXT_PUBLIC_API_URL` env var
- Backend migrations run automatically on startup (in Docker)
