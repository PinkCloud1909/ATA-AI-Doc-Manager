import logging
from typing import TYPE_CHECKING

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import get_request_id

if TYPE_CHECKING:
    from google.cloud.error_reporting import Client as ErrorReportingClient

logger = logging.getLogger(__name__)

# Lazily-initialized Error Reporting client.  Created only when the
# ``google-cloud-error-reporting`` package is installed and a 500-level
# error is encountered.  In local dev the import is skipped gracefully.
_error_client: "ErrorReportingClient | None" = None


def _get_error_client() -> "ErrorReportingClient | None":
    """Return a cached Error Reporting client, or None if unavailable."""
    global _error_client
    if _error_client is not None:
        return _error_client
    try:
        from google.cloud.error_reporting import (  # noqa: PLC0415
            Client as ErrorReportingClient,
        )

        _error_client = ErrorReportingClient()
        logger.info("error_reporting_client_initialized")
        return _error_client
    except ImportError:
        logger.debug("error_reporting_not_available")
    except Exception:
        logger.warning("error_reporting_init_failed", exc_info=True)
    return None


class AppError(Exception):
    status_code = 400
    code = "app_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"


class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class ValidationError(AppError):
    status_code = 422
    code = "validation_error"


class ExternalServiceError(AppError):
    status_code = 502
    code = "external_service_error"


class ConfigurationError(AppError):
    """Raised when the application is misconfigured (e.g. invalid region).

    This is a startup / initialisation error, not a runtime request error.
    The status code 500 reflects that the service cannot operate until the
    configuration is corrected.
    """

    status_code = 500
    code = "configuration_error"


def _build_error_response(status_code: int, code: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": detail,
            "code": code,
            "request_id": get_request_id(),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        logger.warning("application_error", extra={"code": exc.code})
        return _build_error_response(exc.status_code, exc.code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning("request_validation_error", extra={"errors": exc.errors()})
        return _build_error_response(422, "request_validation_error", "Invalid request")

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
        code = "http_error"
        detail = exc.detail if isinstance(exc.detail, str) else "HTTP error"
        logger.warning("http_exception", extra={"status_code": exc.status_code})
        return _build_error_response(exc.status_code, code, detail)

    @app.exception_handler(Exception)
    async def handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", exc_info=exc)
        # Report to Error Reporting so unhandled exceptions appear in the
        # Error Reporting dashboard with automatic grouping and notifications.
        client = _get_error_client()
        if client is not None:
            try:
                client.report_exception()
            except Exception:
                logger.warning("error_reporting_report_failed", exc_info=True)
        return _build_error_response(
            500, "internal_server_error", "Internal server error"
        )
