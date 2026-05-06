"""
main.py
FastAPI application entry point.
"""
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.middleware import register_middleware
from app.api.v1.router import api_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    logger.info("startup", env=settings.APP_ENV, project=settings.GCP_PROJECT_ID)

    # Warm-up: pre-load Vertex AI models (giảm cold start latency)
    try:
        import vertexai
        vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.VERTEX_AI_LOCATION)
        logger.info("vertex_ai_initialized")
    except Exception as e:
        logger.warning("vertex_ai_init_failed", error=str(e))

    yield

    logger.info("shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,    # tắt Swagger trên production
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    # Cloud Run: FE và BE có thể khác domain → cần CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_origin_regex=r"https://.*\.run\.app",   # tất cả Cloud Run services
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Middleware ────────────────────────────────────────────────────────────
    register_middleware(app)

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(api_router)

    # ── Health check ─────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok", "env": settings.APP_ENV}

    return app


app = create_app()
