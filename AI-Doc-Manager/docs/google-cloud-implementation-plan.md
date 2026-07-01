# Google Cloud Production Implementation Plan

**Repository:** ATA-AI-Doc-Manager  
**Date:** 2026-07-01  
**Audience:** AI coding sessions, lead engineers  
**Status:** Draft — awaiting review before implementation

---

## 1. Executive Summary

ATA-AI-Doc-Manager is a document management and RAG Q&A system built with FastAPI (backend), Next.js (frontend), PostgreSQL (database), and ChromaDB / MinIO (local dev vector/object stores). The codebase already has placeholder adapters for GCS, Vertex AI Vector Search, and Vertex AI Gemini, controlled by the `ENV=prod` environment variable. This plan bridges the remaining gaps between the current local Docker Compose setup and a fully production-grade Google Cloud deployment.

---

## 2. Target Architecture

```
+-----------------------------------------------------+
|                   Google Cloud Project               |
|                                                     |
|  +--------------+    HTTPS     +-----------------+ |
|  |  Firebase    |              |  Cloud Run      | |
|  |  Hosting /   |  or Cloud    |  (Frontend      | |
|  |  Cloud Run   |  Run Ingress |  Next.js :8080) | |
|  +--------------+              +--------+--------+ |
|                                         | /api/*    |
|  +--------------------------------------v--------+  |
|  |          Cloud Run (Backend FastAPI :8080)    |  |
|  |  - ENV=prod: GCS adapter, Vertex adapters    |  |
|  |  - Secrets injected as env vars (Secret Mgr) |  |
|  |  - Cloud SQL socket auth (SQL Proxy v2)      |  |
|  +-----+---────────+--────────────────+----------+  |
|        |           |                  |             |
|  +-----v---+  +----v----+  +---------v----------+ |
|  |Cloud SQL|  |Cloud    |  | Vertex AI           | |
|  |Postgres |  |Storage  |  | - Gemini LLM        | |
|  |(private |  |(docs    |  | - Vector Search     | |
|  | IP + SA)|  | bucket) |  |   Index + Endpoint  | |
|  +---------+  +---------+  +---------------------+ |
|                                                     |
|  +----------+  +----------+  +--------------------+ |
|  |Cloud     |  |Secret    |  | Cloud Build +       | |
|  |Tasks     |  |Manager   |  | Artifact Registry   | |
|  |(async    |  |(secrets) |  | (CI/CD pipeline)    | |
|  | vectors) |  +----------+  +--------------------+ |
|  +----------+                                       |
+-----------------------------------------------------+
```

**Service mapping:**

| Layer | Local (Docker Compose) | Production (GCP) |
|---|---|---|
| API backend | Docker `api` container | Cloud Run service |
| Frontend | Docker `frontend` container | Cloud Run or Firebase Hosting |
| Database | PostgreSQL container | Cloud SQL for PostgreSQL 16 |
| Object storage | MinIO container | Cloud Storage bucket |
| Vector store | ChromaDB (persistent) | Vertex AI Vector Search |
| Embeddings / LLM | `google-genai` + `GOOGLE_API_KEY` | Vertex AI Gemini (ADC) |
| Async tasks | Synchronous in request | Cloud Tasks -> Cloud Run worker |
| Secrets | `.env` file | Secret Manager |
| Container registry | Local Docker | Artifact Registry |
| CI/CD | Manual `docker compose` | Cloud Build triggers |

---

## 3. Current State Assessment

### 3.1 What Is Production-Ready

| Component | File(s) | Status |
|---|---|---|
| Adapter abstraction | `shared/interfaces.py`, `shared/adapters/factory.py` | Ready - ENV-based dispatch works |
| GCS adapter | `shared/adapters/gcs_storage_adapter.py` | Exists, has signed URL bug (see gap G-1) |
| Vertex AI LLM adapter | `shared/adapters/vertex_ai_llm_adapter.py` | Uses ADC correctly via `genai.Client(vertexai=True)` |
| Vertex Vector adapter | `shared/adapters/vertex_vector_adapter.py` | Exists, incomplete (text retrieval missing, delete is no-op) |
| Config structure | `core/config.py` | Pydantic settings, no hard-coded secrets, GCP fields present |
| Frontend Dockerfile | `frontend/Dockerfile` | Multi-stage, `standalone` output, PORT=8080 |
| Backend Dockerfile | `backend/Dockerfile` | Functional but needs health probe alignment and non-root user |
| Alembic migrations | `app/alembic/` | Schema-driven, reads `DATABASE_URL` from config |
| RAG agent | `modules/qa/domain/agent.py` | Google ADK, plugs into adapter factory |
| ADK session persistence | `modules/qa/application/services.py` | Uses `DatabaseSessionService` with `asyncpg` |
| FastAPI health endpoints | `main.py` | `/health` and `/ready` (DB ping) |

### 3.2 Current Gaps

| # | Gap | Severity | Files Affected |
|---|---|---|---|
| G-1 | GCS signed URLs fail in Cloud Run without service account key file | CRITICAL | `gcs_storage_adapter.py` |
| G-2 | Cloud SQL connection uses TCP - must use Unix socket or Cloud SQL Python Connector in prod | CRITICAL | `core/config.py`, `core/db.py`, deployment |
| G-3 | `VertexVectorAdapter.semantic_search` returns stub text | CRITICAL | `vertex_vector_adapter.py` |
| G-4 | `VertexVectorAdapter.delete_document` is a no-op (`pass`) | HIGH | `vertex_vector_adapter.py` |
| G-5 | Vectorization is synchronous in-request - will timeout Cloud Run on large documents | HIGH | `vectorization/api/router.py` |
| G-6 | No Cloud Build pipeline or Artifact Registry configuration exists | HIGH | Missing: `cloudbuild.yaml` |
| G-7 | No Cloud SQL instance, bucket, Vector Search index provisioning scripts | HIGH | Missing: `infra/` |
| G-8 | Backend Dockerfile runs as root; no `USER` directive | MEDIUM | `backend/Dockerfile` |
| G-9 | `factory.py` uses `os.getenv("ENV")` rather than `settings.environment` | MEDIUM | `shared/adapters/factory.py` |
| G-10 | `alembic upgrade head` runs inside the app container on startup - unsafe in multi-instance Cloud Run | MEDIUM | `docker-compose.yml`, deployment strategy |
| G-11 | `JWT_SECRET_KEY` is injected as plain env var - must come from Secret Manager | MEDIUM | `.env`, deployment |
| G-12 | `default_admin_password` seeded as plain `admin123` - no prod guard | MEDIUM | `core/config.py`, `scripts/seed.py` |
| G-13 | CORS origins hardcoded to `localhost` in `.env.example` | MEDIUM | `core/config.py` |
| G-14 | Frontend `BACKEND_URL` points to Docker service name - must be Cloud Run URL | MEDIUM | `frontend/Dockerfile`, `next.config.mjs` |
| G-15 | No Cloud Tasks integration for async vectorization | MEDIUM | Missing: `tasks/` module |
| G-16 | `root_agent` uses `gemini-2.0-flash` hardcoded - should use `settings.llm_model` | LOW | `modules/qa/domain/agent.py` |
| G-17 | ChromaDB dependency always installed even in prod image - bloats container | LOW | `backend/pyproject.toml` |
| G-18 | `minio_presigned_expiry_minutes` referenced in `gcs_storage_adapter.py` - wrong config key name | MEDIUM | `gcs_storage_adapter.py` |
| G-19 | No Terraform / Infrastructure-as-Code for GCP resource provisioning | HIGH | Missing |

---

## 4. Required Code Changes

### 4.1 G-1: GCS Signed URLs Without a Key File

**Problem:** `blob.generate_signed_url(version="v4", ...)` requires a service account private key when called outside of GCE/Cloud Run unless you use IAM signing. Cloud Run uses ADC; without configuring the IAM credentials client, the call raises `Unauthorized`.

**Official guidance:** The Cloud Run service account needs `iam.serviceAccounts.signBlob` permission (via `roles/iam.serviceAccountTokenCreator` on itself), then the `google-cloud-storage` library uses ADC automatically for signing.

**Fix** (`backend/app/shared/adapters/gcs_storage_adapter.py`):

```python
# Replace:
return blob.generate_signed_url(version="v4", expiration=ttl, method="GET")

# With:
import google.auth
import google.auth.transport.requests

credentials, _ = google.auth.default()
auth_request = google.auth.transport.requests.Request()
credentials.refresh(auth_request)

return blob.generate_signed_url(
    version="v4",
    expiration=ttl,
    method="GET",
    credentials=credentials,  # ADC-based signing - no key file needed
)
```

**Also fix config key name (G-18):** In `gcs_storage_adapter.py`, `self.settings.minio_presigned_expiry_minutes` should use a dedicated `gcs_presigned_expiry_minutes` setting added to `config.py`.

### 4.2 G-2: Cloud SQL Connection from Cloud Run

**Problem:** Current `DATABASE_URL = postgresql+psycopg://user:pass@host:5432/db` uses TCP. Cloud Run with the Cloud SQL Auth Proxy v2 exposes a Unix socket at `/cloudsql/<CONNECTION_NAME>`.

**Fix** - Add to `core/config.py`:

```python
cloud_sql_connection_name: str | None = None  # e.g. "proj:region:instance"
db_user: str = "postgres"
db_password: str = "postgres"
db_name: str = "dms_backend"
```

**Fix** - Update `core/db.py` to build the correct URL:

```python
def _build_database_url(settings: Settings) -> str:
    if settings.cloud_sql_connection_name:
        # Cloud Run + Cloud SQL Auth Proxy v2 (Unix socket)
        socket_path = f"/cloudsql/{settings.cloud_sql_connection_name}"
        return (
            f"postgresql+psycopg://{settings.db_user}:{settings.db_password}"
            f"@/{settings.db_name}?host={socket_path}"
        )
    return settings.database_url
```

The Cloud Run service must also declare a Cloud SQL connection via `--add-cloudsql-instances`.

**NOTE:** Validate `asyncpg` Unix socket connection pattern in a test environment first - official docs primarily show `psycopg2` and `pg8000` for socket paths.

### 4.3 G-3 & G-4: VertexVectorAdapter - Complete Text Retrieval and Delete

**Problem:** `semantic_search` returns placeholder text; `delete_document` is a no-op.

**Architecture decision:** Vertex AI Vector Search returns only vector IDs, not text. Text chunks must be stored separately in a `document_chunks` PostgreSQL table.

**Fix steps (separate AI session - T-06 through T-09):**
1. Add `document_chunks` table via Alembic migration (columns: `id`, `document_id`, `chunk_index`, `text`, `embedding_model`).
2. In `vectorize_document` service, persist chunks to this table *before* upserting to Vertex.
3. In `VertexVectorAdapter.semantic_search`, after `find_neighbors`, fetch text from `document_chunks` using the returned IDs.
4. In `VertexVectorAdapter.delete_document`, query `document_chunks` for IDs, call `index.remove_datapoints(datapoint_ids=[...])`, then delete rows.

### 4.4 G-5: Async Vectorization via Cloud Tasks

**Problem:** Vectorization is synchronous in the HTTP request. Large PDFs can take 30-120 seconds, exceeding Cloud Run's default request timeout.

**Cloud Tasks task creation pattern:**
```python
from google.cloud import tasks_v2

task = {
    "http_request": {
        "http_method": tasks_v2.HttpMethod.POST,
        "url": f"{settings.worker_service_url}/api/v1/vectorization/worker/{document_id}",
        "oidc_token": {
            "service_account_email": settings.cloud_run_sa_email,
            "audience": settings.worker_service_url,
        },
    }
}
client = tasks_v2.CloudTasksClient()
parent = client.queue_path(settings.gcp_project_id, settings.cloud_tasks_location, settings.cloud_tasks_queue_name)
client.create_task(request={"parent": parent, "task": task})
```

**Changes required:**
1. Add `google-cloud-tasks` to `pyproject.toml`.
2. Add `CLOUD_TASKS_QUEUE_NAME`, `CLOUD_TASKS_LOCATION`, `WORKER_SERVICE_URL`, `CLOUD_RUN_SA_EMAIL` to config.
3. Create `shared/task_publisher.py`.
4. Create `modules/vectorization/api/worker_router.py` (internal-only route, validates OIDC).
5. Change `POST /api/v1/vectorization/{document_id}` to enqueue task and return `202 Accepted`.

### 4.5 G-6: Cloud Build Pipeline

**New file** `cloudbuild.yaml` at repo root:

```yaml
steps:
  # Build backend
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - build
      - -t
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_AR_REPO}/backend:$COMMIT_SHA'
      - ./backend

  # Push backend
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - push
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_AR_REPO}/backend:$COMMIT_SHA'

  # Run migration Cloud Run Job before deploying new revision
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - run
      - jobs
      - execute
      - dms-migrate
      - --wait
      - --region
      - '${_REGION}'

  # Deploy backend to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - run
      - deploy
      - dms-backend
      - --image
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_AR_REPO}/backend:$COMMIT_SHA'
      - --region
      - '${_REGION}'
      - --platform
      - managed
      - --set-env-vars
      - 'ENV=prod,ENVIRONMENT=production'
      - --set-secrets
      - 'JWT_SECRET_KEY=jwt-secret-key:latest,DATABASE_URL=database-url:latest'
      - --add-cloudsql-instances
      - '${PROJECT_ID}:${_REGION}:${_SQL_INSTANCE}'
      - --service-account
      - '${_BACKEND_SA}'

substitutions:
  _REGION: us-central1
  _AR_REPO: dms-repo
  _SQL_INSTANCE: dms-postgres
  _BACKEND_SA: dms-backend@${PROJECT_ID}.iam.gserviceaccount.com
  _BACKEND_URL: https://dms-backend-xxx.run.app

images:
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_AR_REPO}/backend:$COMMIT_SHA'
```

### 4.6 G-8: Backend Dockerfile - Non-Root User and Port Alignment

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

COPY pyproject.toml README.md alembic.ini ./
COPY app ./app
COPY scripts ./scripts

RUN pip install --no-cache-dir .

USER app

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

> **Important:** Cloud Run defaults to port `8080`. The current Dockerfile exposes `8000` and Docker Compose maps `8000:8000`. Update Cloud Run deployment to pass `--port 8080` or use `${PORT}` in CMD. The `PORT` env var is injected automatically by Cloud Run.

### 4.7 G-9: Unify ENV Detection in Factory

```python
# Replace in shared/adapters/factory.py:
env = os.getenv("ENV", "local").lower()

# With:
env = settings.environment.lower()
```

This ensures a single source of truth (`ENVIRONMENT=production` in Secret Manager).

### 4.8 G-10: Alembic Migration Strategy for Cloud Run

Run migrations as a separate Cloud Run Job before deploying the service revision:

1. Create a Cloud Run Job `dms-migrate` pointing to the same backend image with `CMD ["alembic", "upgrade", "head"]`.
2. Execute `gcloud run jobs execute dms-migrate --wait` in `cloudbuild.yaml` before the service deploy step.
3. Remove `alembic upgrade head` from the Docker Compose `command` only for production; keep it for local dev.

### 4.9 G-16: Use Settings for Agent Model Name

```python
# modules/qa/domain/agent.py
from app.core.config import get_settings

_settings = get_settings()

root_agent = Agent(
    model=_settings.llm_model,  # was: hardcoded "gemini-2.0-flash"
    ...
)
```

---

## 5. Required Google Cloud Services

| Service | Purpose | Notes |
|---|---|---|
| **Cloud Run** | Backend API + Frontend | Min instances: 1 for backend; 0 for frontend |
| **Cloud SQL (PostgreSQL 16)** | Primary database + ADK session store | Private IP, Cloud SQL Auth Proxy v2, generation 2 Cloud Run execution environment |
| **Cloud Storage** | Document file storage | Uniform bucket-level access, no public objects, lifecycle policy |
| **Vertex AI - Gemini** | Embeddings + LLM generation | Models: `gemini-embedding-2`, `gemini-2.5-flash` |
| **Vertex AI - Vector Search** | Semantic similarity index | Streaming index, `COSINE_DISTANCE`, dimension = 3072 (gemini-embedding-2) |
| **Cloud Tasks** | Async vectorization queue | HTTP target, OIDC auth to Cloud Run worker |
| **Secret Manager** | Secrets storage | `JWT_SECRET_KEY`, `DATABASE_URL`, `DEFAULT_ADMIN_PASSWORD`, others |
| **Artifact Registry** | Container images | Docker repo per region |
| **Cloud Build** | CI/CD pipeline | Trigger on push to `main` branch |
| **IAM** | Service accounts + roles | Least privilege; separate SA per service |
| **VPC / Private Service Connect** | Cloud SQL private IP | For Vertex Vector Search private endpoint (optional but recommended) |

---

## 6. Required Environment Variables

### 6.1 Backend Cloud Run Service (non-secret)

| Variable | Value in Production | Notes |
|---|---|---|
| `ENVIRONMENT` | `production` | Triggers JWT key validation |
| `ENV` | `prod` | Factory dispatch to GCS/Vertex adapters (consolidate with ENVIRONMENT per G-9) |
| `GCP_PROJECT_ID` | `<your-project-id>` | Must not be hardcoded |
| `GCP_LOCATION` | `us-central1` | Or your chosen region |
| `GCS_BUCKET_NAME` | `dms-documents-prod` | Use unique name, not generic `documents` |
| `VERTEX_INDEX_ID` | `<index-id>` | Set after Vertex index is created |
| `VERTEX_INDEX_ENDPOINT_ID` | `<endpoint-id>` | Set after endpoint is deployed |
| `VERTEX_DEPLOYED_INDEX_ID` | `<deployed-index-id>` | Set after index is deployed to endpoint |
| `CLOUD_SQL_CONNECTION_NAME` | `proj:region:instance` | Required for Unix socket connection |
| `DB_USER` | `dms_user` | Cloud SQL DB user (not `postgres`) |
| `DB_NAME` | `dms_backend` | Cloud SQL database name |
| `EMBEDDING_MODEL` | `gemini-embedding-2` | |
| `LLM_MODEL` | `gemini-2.5-flash` | |
| `CORS_ALLOWED_ORIGINS` | `https://your-frontend-domain.com` | No wildcard in production |
| `CLOUD_TASKS_QUEUE_NAME` | `dms-vectorization` | Required for async vectorization |
| `CLOUD_TASKS_LOCATION` | `us-central1` | |
| `WORKER_SERVICE_URL` | `https://dms-backend-xxx.run.app` | Self-referential for Cloud Tasks |
| `CLOUD_RUN_SA_EMAIL` | `dms-backend@proj.iam.gserviceaccount.com` | For OIDC token in Cloud Tasks |
| `PORT` | `8080` | Injected by Cloud Run automatically |

### 6.2 Frontend Cloud Run Service (non-secret)

| Variable | Value in Production | Notes |
|---|---|---|
| `BACKEND_URL` | `https://dms-backend-xxx.run.app` | Internal VPC or public Cloud Run URL |
| `NEXT_PUBLIC_API_URL` | `/api/v1` | Relative - fronted by Next.js rewrite proxy |
| `GCS_BUCKET_NAME` | `dms-documents-prod` | Passed as build arg for next.config.mjs |
| `GCP_PROJECT_ID` | `<your-project-id>` | Passed as build arg |

> **Warning:** Do not expose `NEXT_PUBLIC_FIREBASE_*` credentials unless Firebase Auth is actually implemented. The frontend `.env.example` references Firebase Auth, but the backend currently uses its own JWT system. Align auth strategy before deploying.

---

## 7. Required Secrets (Secret Manager)

| Secret Name | Description | Who Accesses |
|---|---|---|
| `jwt-secret-key` | JWT signing secret (>=32 chars, random) | Backend Cloud Run |
| `database-url` | Full `postgresql+psycopg://...` connection string | Backend Cloud Run |
| `db-password` | Cloud SQL database user password | Backend Cloud Run |
| `default-admin-password` | Initial admin seed password | Backend Cloud Run (startup only) |
| `google-api-key` | `GOOGLE_API_KEY` for local dev adapter; not needed in prod | Backend dev only |

**Secret Manager IAM:**
- Backend service account must have `roles/secretmanager.secretAccessor` on each secret.
- Secrets are injected as environment variables via Cloud Run's `--set-secrets` flag.
- Pin to specific versions (not `latest`) for env-var injection per Google's recommendation.

**Secret Manager injection syntax:**
```bash
gcloud run services update dms-backend \
  --set-secrets=JWT_SECRET_KEY=jwt-secret-key:5,DATABASE_URL=database-url:3
```

---

## 8. Required IAM Service Accounts and Roles

| Service Account | Roles Required |
|---|---|
| `dms-backend@PROJECT.iam.gserviceaccount.com` | `roles/cloudsql.client`, `roles/storage.objectAdmin`, `roles/aiplatform.user`, `roles/cloudtasks.enqueuer`, `roles/secretmanager.secretAccessor`, `roles/iam.serviceAccountTokenCreator` (self, for GCS signed URLs) |
| `dms-frontend@PROJECT.iam.gserviceaccount.com` | Minimal permissions - no GCP API calls from frontend container |
| `dms-cloudbuild@PROJECT.iam.gserviceaccount.com` | `roles/run.developer`, `roles/iam.serviceAccountUser`, `roles/artifactregistry.writer`, `roles/cloudsql.admin` (for migrate job only) |

> **Caution:** The backend service account needs `iam.serviceAccounts.signBlob` on **itself** to generate GCS signed URLs without a key file. This is granted by assigning `roles/iam.serviceAccountTokenCreator` to the service account on itself, not project-wide.

---

## 9. Deployment Order

Execute these steps sequentially in a first-time production deployment:

1. **Create GCP project** and enable APIs:
   ```
   cloudresourcemanager, run, sqladmin, storage, aiplatform, cloudtasks,
   secretmanager, artifactregistry, cloudbuild, iam
   ```

2. **Create service accounts** with roles from section 8.

3. **Create Cloud SQL instance** (PostgreSQL 16, private IP, `us-central1`).
   - Create database `dms_backend` and user `dms_user`.
   - Store connection string in Secret Manager as `database-url`.

4. **Create Cloud Storage bucket** (`dms-documents-prod`).
   - Set uniform bucket-level access.
   - Add lifecycle rule: delete incomplete multipart uploads after 1 day.

5. **Create Vertex AI Vector Search index** (streaming, `COSINE_DISTANCE`, 3072 dims).
   - Create an `IndexEndpoint` (public or private).
   - Deploy index to endpoint.
   - Store `VERTEX_INDEX_ID`, `VERTEX_INDEX_ENDPOINT_ID`, `VERTEX_DEPLOYED_INDEX_ID` in Cloud Run env vars.

6. **Create Cloud Tasks queue** `dms-vectorization` in `us-central1`.

7. **Store all secrets** in Secret Manager (section 7).

8. **Create Artifact Registry Docker repository** (`dms-repo`).

9. **Apply code changes** from section 4 (G-1 through G-18).

10. **Build and push backend image** to Artifact Registry.

11. **Run Cloud Run Job** (`dms-migrate`) to execute `alembic upgrade head`.

12. **Run Cloud Run Job** (`dms-seed`) to execute `scripts/seed.py` (first deploy only).

13. **Deploy backend Cloud Run service** with all env vars and secrets.

14. **Deploy frontend Cloud Run service** (or Firebase Hosting) with `BACKEND_URL` pointing to backend.

15. **Create Cloud Build trigger** on `main` branch push.

16. **Smoke test** all endpoints via `/health`, `/ready`, and the API.

---

## 10. Implementation Phases

### Phase 1 - Foundation (prerequisite for all else)

**Goal:** Code is production-safe with no secrets in env files, correct port, non-root container.

**Tasks:**
- [ ] Fix backend Dockerfile: non-root user, `PORT=8080`, use `${PORT}` in CMD (G-8)
- [ ] Align `ENV` vs `ENVIRONMENT` in factory.py (G-9)
- [ ] Fix `gcs_storage_adapter.py` to use ADC-based signed URL signing (G-1, G-18)
- [ ] Add `CLOUD_SQL_CONNECTION_NAME` support to `config.py` and `db.py` (G-2)
- [ ] Fix agent model to use `settings.llm_model` (G-16)
- [ ] Add `gcs_presigned_expiry_minutes` config key (G-18)

**Acceptance:** Backend image builds cleanly, `ENV=prod` activates GCS and Vertex adapters, signed URLs work in Cloud Run with ADC.

---

### Phase 2 - Vertex Vector Search: Complete Implementation

**Goal:** Vertex AI Vector Search is fully functional end-to-end.

**Tasks:**
- [ ] Add `document_chunks` Alembic migration (id, document_id, chunk_index, text, embedding_model, vectorized_at)
- [ ] Update `vectorize_document` service to persist chunks to PostgreSQL before upserting to Vertex
- [ ] Implement `VertexVectorAdapter.semantic_search`: after `find_neighbors`, JOIN with `document_chunks` by datapoint ID to return actual text (G-3)
- [ ] Implement `VertexVectorAdapter.delete_document`: query `document_chunks` for chunk IDs, call `index.remove_datapoints`, delete DB rows (G-4)
- [ ] Write unit tests for the completed adapter (mock Vertex calls)
- [ ] Provision Vertex AI Vector Search index (streaming, `COSINE_DISTANCE`, 3072 dims) and update env vars

**Acceptance:** Document upload -> vectorize -> QA chat returns actual document content in production.

---

### Phase 3 - Cloud Tasks Async Vectorization

**Goal:** Vectorization is decoupled from the HTTP request; bulk operations don't timeout.

**Tasks:**
- [ ] Add `google-cloud-tasks` to `pyproject.toml`
- [ ] Add Cloud Tasks config fields to `config.py`
- [ ] Create `shared/task_publisher.py` with `enqueue_vectorization_task(document_id)`
- [ ] Create `modules/vectorization/api/worker_router.py` (internal-only endpoint, validates Cloud Tasks OIDC)
- [ ] Refactor `POST /api/v1/vectorization/{document_id}` to enqueue task -> return `202 Accepted`
- [ ] Refactor bulk endpoint similarly
- [ ] Create Cloud Tasks queue `dms-vectorization` in GCP

**Acceptance:** `POST /vectorization/{id}` returns 202 in <1s; vectorization completes asynchronously.

---

### Phase 4 - CI/CD and Infrastructure as Code

**Goal:** Repeatable, automated deployments.

**Tasks:**
- [ ] Write `cloudbuild.yaml` (section 4.5)
- [ ] Write `infra/` Terraform or `gcloud` shell scripts for all GCP resources
- [ ] Create Cloud Build trigger on `main` branch
- [ ] Extract `alembic upgrade head` into Cloud Run Job (`dms-migrate`) called from `cloudbuild.yaml`
- [ ] Document all substitution variables and Cloud Build SA permissions

**Acceptance:** `git push origin main` triggers an automated build, migration, and deployment.

---

### Phase 5 - Hardening and Monitoring

**Goal:** Production-grade observability and security.

**Tasks:**
- [ ] Add Cloud Logging structured log export (already using JSON logging)
- [ ] Create Cloud Monitoring alerting policies (error rate, latency p99, memory)
- [ ] Enable Cloud Armor or rate-limiting on Cloud Run ingress
- [ ] Implement startup probe in Cloud Run deployment (HTTP `/health`, initial delay 10s)
- [ ] Enable VPC-native networking and private Cloud SQL IP
- [ ] Review and tighten IAM bindings (remove any broad `Editor` roles)
- [ ] Add `google-cloud-secret-manager` to optional dev deps; document local secret access
- [ ] Set up budget alerts in Billing

---

## 11. Risks and Open Questions

### 11.1 Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Vertex AI Vector Search index provisioning cost and latency | Medium | High | Index creation can take 30-60 min; plan ahead. Use streaming index to allow immediate upsert after creation. |
| ADC signed URL permissions not granted | Medium | High | Test locally with `gcloud auth application-default login` before deploying; add `roles/iam.serviceAccountTokenCreator` (self). |
| Cloud SQL socket connection breaks during migration | Low | High | Use Cloud SQL connector library as alternative; test socket path `/cloudsql/PROJECT:REGION:INSTANCE`. |
| `asyncpg` + Cloud SQL Unix socket compatibility | Medium | High | Official docs only show `pg8000` and `psycopg2` for Unix socket snippets. Validate `asyncpg` socket connection pattern in a test environment first. |
| ADK `DatabaseSessionService` creates tables on first run - may conflict with Alembic | Medium | Medium | Check ADK-created tables against Alembic migrations; add ADK tables to migration or mark as skip. |
| Vertex AI Vector Search does not store text - retrieval requires Postgres join | Certain | High | Phase 2 mitigates this; do not deploy Phase 1 to prod use without Phase 2. |
| Frontend Firebase Auth vs backend JWT mismatch | Medium | High | Frontend `.env.example` references Firebase Auth; backend uses PyJWT. Clarify auth strategy before prod. |
| MinIO object references (`minio://bucket/key`) in DB - cannot be read by GCS adapter | Certain | High | GCS adapter expects `gcs://` prefix; on first prod deploy, all existing documents' `file_link` values must be migrated or re-uploaded. |

### 11.2 Open Questions

1. **Auth strategy:** Will production authentication use Firebase Auth (frontend ID token -> backend verification), the current PyJWT-based system, or IAP (Identity-Aware Proxy)? This impacts frontend config and backend `security.py`.

2. **Frontend deployment target:** Cloud Run vs Firebase Hosting? Firebase Hosting is simpler for Next.js static export but requires `output: "export"` (incompatible with API routes). Cloud Run supports the current `standalone` mode. Recommend Cloud Run.

3. **Vertex AI Vector Search endpoint type:** Public endpoint (simpler, slightly less secure) vs private VPC endpoint (requires Shared VPC, more setup). For an enterprise DMS, private is recommended.

4. **Multi-tenancy:** Does `filter_document_ids` in `IVectorStore.semantic_search` need to filter by user/org in addition to document? This determines whether Vertex AI `restricts` filtering is needed.

5. **GCS bucket region:** Must be co-located with Cloud Run and Vertex AI regions to minimize latency and avoid cross-region egress costs.

6. **Alembic + ADK sessions:** Does `DatabaseSessionService` auto-create its own tables? If yes, those tables need to be incorporated into Alembic or ignored.

7. **Document migration on first prod deploy:** How will existing documents with `minio://` references be handled? Options: re-upload to GCS, or maintain both adapters and route on prefix.

8. **Embedding model dimension:** `gemini-embedding-2` produces 3072-dimensional vectors. The Vertex AI index must be created with `dimensions=3072`. Verify this is the correct dimension for the model version in use.

---

## 12. Follow-Up Task Index

Each item below is scoped for a separate AI coding session:

| ID | Task | Phase | Estimated Complexity |
|---|---|---|---|
| T-01 | Fix GCS signed URL to use ADC (G-1, G-18) | 1 | Small |
| T-02 | Fix backend Dockerfile: non-root user, PORT=8080 (G-8) | 1 | Small |
| T-03 | Unify ENV vs ENVIRONMENT in factory.py (G-9) | 1 | Trivial |
| T-04 | Add Cloud SQL Unix socket support to config + db.py (G-2) | 1 | Medium |
| T-05 | Use settings.llm_model in agent.py (G-16) | 1 | Trivial |
| T-06 | Alembic migration: add `document_chunks` table | 2 | Medium |
| T-07 | Update vectorize_document service to persist chunks to Postgres | 2 | Medium |
| T-08 | Implement VertexVectorAdapter.semantic_search with DB fetch (G-3) | 2 | Medium |
| T-09 | Implement VertexVectorAdapter.delete_document (G-4) | 2 | Small |
| T-10 | Unit tests for completed VertexVectorAdapter | 2 | Medium |
| T-11 | Add Cloud Tasks async vectorization (G-5, G-15) | 3 | Large |
| T-12 | Write cloudbuild.yaml (G-6) | 4 | Medium |
| T-13 | Write infra/ provisioning scripts or Terraform (G-7, G-19) | 4 | Large |
| T-14 | Extract alembic migration to Cloud Run Job (G-10) | 4 | Medium |
| T-15 | Resolve frontend auth strategy (Firebase vs JWT) | 5 | Large |
| T-16 | Cloud Monitoring alerting and dashboards | 5 | Medium |
| T-17 | Remove chromadb from prod image (optional dep split) (G-17) | 5 | Small |

---

## 13. Local Development Preservation

All changes must remain backward compatible with Docker Compose local development:

- `ENVIRONMENT=local` (or unset) continues to use MinIO + ChromaDB.
- `ENVIRONMENT=production` activates GCS + Vertex AI.
- Cloud SQL socket path only activates when `CLOUD_SQL_CONNECTION_NAME` is set; otherwise falls back to `DATABASE_URL`.
- Alembic migration Cloud Run Job runs only in CI/CD; `docker compose up` continues to run `alembic upgrade head` on startup (acceptable for single-instance local use).
- `.env.example` files remain the single source of truth for local variables; Cloud Run env vars and Secret Manager are production-only.

---

*Generated by: Antigravity (Google DeepMind) based on full repository audit + Google Developer Knowledge MCP*
*Library versions audited: google-cloud-storage>=3.0.0, google-cloud-aiplatform>=1.150.0, google-genai>=1.75.0, google-adk>=1.32.0*
