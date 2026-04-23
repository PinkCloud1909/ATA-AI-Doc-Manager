import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db_session, ping_database
from app.core.exceptions import register_exception_handlers
from app.core.logging import clear_request_id, configure_logging, set_request_id
from app.modules.documents.api.router import approvals_router, documents_router
from app.modules.iam.api.router import router as auth_router
from app.modules.reviews.api.router import router as reviews_router
from app.shared.schemas import HealthResponse, ReadyResponse
from app.shared.utils import generate_request_id

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("application_startup", extra={"environment": settings.environment})
    yield
    logger.info("application_shutdown")


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)
register_exception_handlers(app)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(approvals_router)
app.include_router(reviews_router)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    clear_request_id()
    return response


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    logger.info("health_check", extra={"path": "/health"})
    return HealthResponse()


@app.get("/ready", response_model=ReadyResponse, tags=["system"])
def ready(session: Session = Depends(get_db_session)) -> ReadyResponse:
    try:
        ping_database(session)
    except SQLAlchemyError as exc:
        logger.warning("readiness_failed", extra={"reason": str(exc)})
        raise HTTPException(status_code=503, detail="Database is not ready") from exc

    logger.info("readiness_check", extra={"path": "/ready"})
    return ReadyResponse(checks={"database": "ok"})
