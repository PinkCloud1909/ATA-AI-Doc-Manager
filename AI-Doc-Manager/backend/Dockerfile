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

COPY pyproject.toml README.md alembic.ini ./
COPY app ./app
COPY scripts ./scripts

RUN pip install --no-cache-dir .

# Switch to the non-root user before starting the process.
USER app

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
