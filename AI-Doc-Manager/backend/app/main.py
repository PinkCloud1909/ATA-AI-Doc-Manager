import logging
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db_session, ping_database
from app.core.exceptions import register_exception_handlers
from app.core.logging import (
    clear_request_id,
    clear_trace_context,
    configure_logging,
    set_request_id,
    set_trace_context,
)
from app.modules.documents.api.router import approvals_router, documents_router
from app.modules.iam.api.router import router as auth_router
from app.modules.iam.api.admin_router import admin_router
from app.modules.qa.api.router import router as qa_router
from app.modules.reviews.api.router import router as reviews_router
from app.modules.rag.api.router import router as rag_router
from app.modules.rag.api.worker_router import worker_router as rag_worker_router
from app.modules.runbooks.api.router import router as runbooks_router
from app.shared.openapi_helpers import (
    APP_DESCRIPTION,
    PROBE_RESPONSES,
    TAG_METADATA,
)
from app.shared.schemas import HealthResponse, ReadyResponse
from app.shared.utils import generate_request_id

settings = get_settings()
configure_logging(settings.log_level, project_id=settings.gcp_project_id or "")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("application_startup", extra={"environment": settings.environment})
    yield
    # Graceful shutdown: dispose of SQLAlchemy engine connection pools so
    # connections are properly closed before the Cloud Run container stops.
    # Cloud Run sends SIGTERM and allows up to 10 s for graceful shutdown;
    # failing to close connections leaves half-open sockets on the database
    # side that eventually time out (OS default ~2 hours).
    from app.core.db import get_engine  # noqa: PLC0415

    try:
        get_engine().dispose()
        logger.info("engine_pool_disposed")
    except Exception:
        logger.warning("engine_pool_dispose_failed", exc_info=True)
    logger.info("application_shutdown")


app = FastAPI(
    title=settings.app_name,
    description=APP_DESCRIPTION,
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
    contact={
        "name": "DMS Development Team",
        "url": "https://github.com/your-org/dms-backend",
    },
    license_info={
        "name": "Proprietary",
    },
    openapi_tags=TAG_METADATA,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── OpenAPI 3.1 schema customisation ──────────────────────────────────────
# Register the JWT Bearer security scheme and apply it globally so every
# authenticated endpoint shows the lock icon in Swagger UI.  Endpoints that
# do *not* require auth (health, login, register) explicitly override with
# ``security=[{}]`` in their decorator to clear the global requirement.

_original_openapi = app.openapi


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title or "",
        version=app.version or "",
        description=app.description or "",
        routes=app.routes,
        tags=app.openapi_tags,
    )
    openapi_schema.setdefault("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": (
                "JWT access token obtained from POST /api/v1/auth/login.  "
                "Prefix the token value with nothing — just the raw JWT string."
            ),
        }
    }
    # Apply globally — every endpoint requires auth unless overridden.
    openapi_schema.setdefault("security", [])
    openapi_schema["security"].append({"BearerAuth": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]


register_exception_handlers(app)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(documents_router)
app.include_router(approvals_router)
app.include_router(reviews_router)
app.include_router(qa_router)
app.include_router(rag_router)
app.include_router(rag_worker_router)
app.include_router(runbooks_router)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    # Cloud Run adds X-Cloud-Trace-Context on incoming requests.
    # Populate the trace context so structured logs include
    # logging.googleapis.com/trace for request-log correlation.
    set_trace_context(
        request.headers.get("X-Cloud-Trace-Context"),
        project_id=settings.gcp_project_id,
    )
    start = time.perf_counter()
    try:
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id

        # ── Structured request log with httpRequest for correlation ──────
        # Populating the ``httpRequest`` field enables the parent-child log
        # hierarchy in Cloud Logs Explorer: expanding a request log shows
        # all container logs emitted during that request.
        # https://cloud.google.com/logging/docs/structured-logging#special-fields
        http_request: dict[str, object] = {
            "requestMethod": request.method,
            "requestUrl": str(request.url),
            "status": response.status_code,
            # Cloud Logging expects latency as a Duration string (e.g. "1.234s").
            "latency": f"{duration_ms / 1000:.3f}s",
        }
        user_agent = request.headers.get("User-Agent")
        if user_agent:
            http_request["userAgent"] = user_agent
        referer = request.headers.get("Referer")
        if referer:
            http_request["referer"] = referer

        logger.info(
            "request_completed",
            extra={
                "httpRequest": http_request,
                "duration_ms": duration_ms,
            },
        )
        return response
    finally:
        clear_request_id()
        clear_trace_context()


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["system"],
    summary="Liveness probe",
    description=(
        "Returns 200 OK to indicate the service process is running.  "
        "Does **not** verify database connectivity — use `/ready` for "
        "that purpose.  Intended for container orchestrators and load "
        "balancer health checks."
    ),
    response_description="Service is alive",
)
def health() -> HealthResponse:
    logger.info("health_check", extra={"path": "/health"})
    return HealthResponse()


@app.get(
    "/ready",
    response_model=ReadyResponse,
    tags=["system"],
    summary="Readiness probe",
    description=(
        "Verifies that both the synchronous (write-path) and asynchronous "
        "(chat-path) database connections are reachable.  Returns 503 if "
        "either is down.  Intended for load balancer readiness checks "
        "and container orchestration startup probes."
    ),
    response_description="All dependencies are reachable",
    responses=PROBE_RESPONSES,
)
async def ready(session: Session = Depends(get_db_session)) -> ReadyResponse:
    try:
        ping_database(session)
    except SQLAlchemyError as exc:
        logger.warning("readiness_failed_sync", extra={"reason": str(exc)})
        raise HTTPException(status_code=503, detail="Sync database is not ready") from exc

    try:
        from app.modules.qa.api.router import chat_service
        from sqlalchemy import text
        async with chat_service.session_service.db_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning("readiness_failed_async", extra={"reason": str(exc)})
        raise HTTPException(status_code=503, detail="Async database is not ready") from exc

    logger.info("readiness_check", extra={"path": "/ready"})
    return ReadyResponse(checks={"database": "ok", "chat_database": "ok"})
