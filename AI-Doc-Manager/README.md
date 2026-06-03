# AI-Doc-Manager

AI document management platform with document upload/versioning, chat and voice chat, runbook generation, document scoring, and approval workflow.

## Project Structure

```text
AI-Doc-Manager/
  backend/          FastAPI backend, SQLAlchemy models, Alembic migrations, tests
  frontend/         Next.js frontend application
  docs/             Architecture, API, setup, and testing guides
  docker-compose.yml
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

Frontend: http://localhost:3000

## Docker

```powershell
cd C:\Users\ADMIN\Desktop\TKTL\AI-Doc-Manager
docker compose up --build
```

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [API Endpoints](docs/API_ENDPOINTS.md)
- [Run Guide](docs/RUN_GUIDE.md)
- [Quick Setup](docs/QUICK_SETUP.md)
- [Frontend/Backend Guide](docs/FRONTEND_BACKEND_GUIDE.md)
- [Test API Guide](docs/TEST_API_GUIDE.md)
