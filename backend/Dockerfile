FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Cloud Run injects PORT automatically; default to 8080 so local Docker
# runs on the same port without extra configuration.
ENV PORT=8080

# Create a non-root system user and group to run the application.
# Running as root inside a container is a security anti-pattern for Cloud Run.
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Install the package and its dependencies.
COPY pyproject.toml README.md alembic.ini ./
COPY app ./app
COPY scripts ./scripts

RUN pip install --no-cache-dir .

# Switch to the non-root user before starting the process.
USER app

# ── API server (default) ───────────────────────────────────────────────
# Runs uvicorn on 0.0.0.0:8080.  Cloud Run injects PORT=8080 automatically.
# Uses `python -m uvicorn` directly (no shell wrapper) because `sh -c` in the
# slim image exits 0 silently under Cloud Run Gen 2 with the non-root `app`
# user.  The direct exec form ensures uvicorn becomes PID 1 and receives
# SIGTERM for Cloud Run's 10-second graceful-shutdown window.
#
# Database migrations MUST be run separately (Cloud Run Job or CI/CD step),
# never as part of the normal container startup — concurrent starts of
# multiple Cloud Run instances would race on DDL.
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-graceful-shutdown", "9"]

# ── Migration Job override ──────────────────────────────────────────────
# To run this image as a one-shot Cloud Run Job that applies migrations and
# seeds bootstrap data, override the entrypoint:
#
#   gcloud run jobs execute dms-migrate \
#       --image REGION-docker.pkg.dev/PROJECT/dms/backend:TAG \
#       --set-env-vars=DATABASE_URL=...,ASYNC_DATABASE_URL=... \
#       --task-override=--command="python scripts/run_migrations.py"
#
# Or in Cloud Build / CI/CD:
#   docker run --rm \
#       -e DATABASE_URL=postgresql+psycopg://user:pass@host/db \
#       -e ASYNC_DATABASE_URL=postgresql+asyncpg://user:pass@host/db \
#       IMAGE python scripts/run_migrations.py
