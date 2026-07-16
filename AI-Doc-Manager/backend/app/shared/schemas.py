from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error envelope returned by all error responses."""

    detail: str = Field(
        description="Human-readable description of the error",
        examples=["The requested resource was not found"],
    )
    code: str = Field(
        description="Machine-readable error code (e.g. 'not_found', 'unauthorized')",
        examples=["not_found"],
    )
    request_id: str | None = Field(
        default=None,
        description="Unique request identifier from the X-Request-ID header, for tracing",
        examples=["a1b2c3d4e5f6a7b8"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "The requested resource was not found",
                "code": "not_found",
                "request_id": "a1b2c3d4e5f6a7b8",
            }
        }
    }


class HealthResponse(BaseModel):
    """Response for the liveness probe (GET /health)."""

    status: str = Field(
        default="ok",
        description="Always 'ok' when the service process is running",
        examples=["ok"],
    )

    model_config = {
        "json_schema_extra": {"example": {"status": "ok"}}
    }


class ReadyResponse(BaseModel):
    """Response for the readiness probe (GET /ready)."""

    status: str = Field(
        default="ready",
        description="Always 'ready' when all dependencies are reachable",
        examples=["ready"],
    )
    checks: dict[str, str] = Field(
        description=(
            "Per-dependency health status.  Each key is a dependency name "
            "(e.g. 'database', 'chat_database') and each value is 'ok' or an error message."
        ),
        examples=[{"database": "ok", "chat_database": "ok"}],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "ready",
                "checks": {"database": "ok", "chat_database": "ok"},
            }
        }
    }
