"""OIDC ID token verification for the internal worker endpoint.

Cloud Tasks attaches a Google-signed OIDC ID token in the
``Authorization: Bearer <token>`` header when it calls the worker
URL with an ``oidc_token`` configured (see task_publisher.py).

Because the backend Cloud Run service is publicly invokable (to serve
user-facing APIs), Cloud Run does NOT automatically validate OIDC
tokens — that automatic validation only applies to services deployed
with ``--no-allow-unauthenticated``.  We therefore verify the token
explicitly here.

Verification steps
------------------
1. Extract the Bearer token from the Authorization header.
2. Verify the token signature using Google's JWKS endpoint (cached by
   the google-auth library after the first request).
3. Assert the ``aud`` (audience) claim matches the Cloud Run service
   URL (``WORKER_SERVICE_URL``).
4. Assert the ``email`` claim matches the configured Cloud Tasks
   service account (``CLOUD_RUN_SA_EMAIL``) and that ``email_verified``
   is True.

Local development bypass
------------------------
When ``is_async_mode()`` is False, the check is skipped entirely.
Cloud Tasks never calls the worker endpoint in local Docker Compose.

Raises
------
fastapi.HTTPException 401
    If the token is missing, invalid, expired, has a wrong audience,
    or the email claim does not match the expected service account.
"""

import logging
from functools import cache

import google.auth.transport.requests
import google.oauth2.id_token
from fastapi import HTTPException, Request

from app.core.config import Settings
from app.shared.task_publisher import is_async_mode

logger = logging.getLogger(__name__)


@cache
def _get_http_request() -> google.auth.transport.requests.Request:
    """Return the cached transport used by verify_oauth2_token."""
    return google.auth.transport.requests.Request()


def verify_worker_token(request: Request, settings: Settings) -> None:
    """Verify the Cloud Tasks OIDC token on the incoming request.

    No-ops in local development (when ``is_async_mode`` is False).

    Args:
        request:  The incoming FastAPI ``Request``.
        settings: The resolved ``Settings`` instance.

    Raises:
        HTTPException: 401 if the token is absent or invalid.
    """
    if not is_async_mode(settings):
        return

    auth_header: str = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        logger.warning(
            "worker_auth_rejected_missing_token",
            extra={"path": str(request.url)},
        )
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = auth_header.removeprefix("Bearer ")
    audience = (settings.worker_service_url or "").rstrip("/")

    try:
        id_info: dict = google.oauth2.id_token.verify_oauth2_token(
            token, _get_http_request(), audience=audience
        )
    except Exception as exc:
        logger.warning(
            "worker_auth_token_invalid",
            extra={"reason": str(exc)},
        )
        raise HTTPException(status_code=401, detail="Invalid bearer token") from exc

    expected_email = settings.cloud_run_sa_email
    if not expected_email:
        logger.error("worker_auth_missing_sa_email_config")
        raise HTTPException(
            status_code=503,
            detail="Server misconfiguration: CLOUD_RUN_SA_EMAIL not set",
        )

    token_email: str = id_info.get("email", "")
    email_verified: bool = id_info.get("email_verified", False)

    if not email_verified or token_email != expected_email:
        logger.warning(
            "worker_auth_rejected_wrong_email",
            extra={"token_email": token_email, "expected": expected_email},
        )
        raise HTTPException(status_code=401, detail="Unauthorized caller")

    logger.debug(
        "worker_auth_ok",
        extra={"email": token_email},
    )
