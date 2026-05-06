# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder
WORKDIR /app

# System deps cho pdfminer + python-docx
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runner ───────────────────────────────────────────────────────────
FROM python:3.12-slim AS runner
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY . .

# Cloud Run inject PORT env var
ENV PORT=8080
EXPOSE 8080

# Chạy alembic migrate rồi start uvicorn
CMD alembic upgrade head && \
    uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT} \
    --workers 1 \
    --loop uvloop \
    --http httptools
