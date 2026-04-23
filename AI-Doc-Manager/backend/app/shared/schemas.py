from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str
    code: str
    request_id: str | None = None


class HealthResponse(BaseModel):
    status: str = Field(default="ok")


class ReadyResponse(BaseModel):
    status: str = Field(default="ready")
    checks: dict[str, str]
