"""Unit tests for worker_auth.verify_worker_token.

All google-auth calls are mocked so these tests run without network access.
google-auth IS installed as a transitive dep, so we patch through the
worker_auth module's own import reference instead of injecting sys.modules stubs.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Patch through the worker_auth module's own attribute reference so the patch
# works regardless of whether google-auth is installed or not.
_VERIFY_PATH = "app.modules.rag.api.worker_auth.google.oauth2.id_token.verify_oauth2_token"
_ASYNC_MODE_PATH = "app.modules.rag.api.worker_auth.is_async_mode"
_HTTP_REQ_PATH = "app.modules.rag.api.worker_auth._get_http_request"


def _settings(**overrides):
    defaults = {
        "environment": "production",
        "cloud_tasks_queue_name": "dms-vectorization",
        "cloud_tasks_location": "us-central1",
        "worker_service_url": "https://dms-backend.run.app",
        "cloud_run_sa_email": "tasks-sa@project.iam.gserviceaccount.com",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.fixture(autouse=True)
def _reset_http_singleton():
    """Reset the lazy transport singleton between tests."""
    import app.modules.rag.api.worker_auth as wa
    wa._get_http_request.cache_clear()
    yield
    wa._get_http_request.cache_clear()


def _make_request(auth_header: str | None = None) -> MagicMock:
    req = MagicMock()
    headers = {}
    if auth_header is not None:
        headers["Authorization"] = auth_header
    req.headers = headers
    req.url = "https://dms-backend.run.app/api/v1/vectorization/worker/abc"
    return req


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestVerifyWorkerToken:
    def test_bypassed_in_local_mode(self):
        """No check should run when is_async_mode returns False."""
        from app.modules.rag.api.worker_auth import verify_worker_token

        request = _make_request()  # no Authorization header
        settings = _settings(environment="local", cloud_tasks_queue_name=None)

        with patch(_ASYNC_MODE_PATH, return_value=False):
            # Should return None without raising
            assert verify_worker_token(request, settings) is None

    def test_raises_401_when_no_auth_header(self):
        """Missing Authorization header → 401."""
        from app.modules.rag.api.worker_auth import verify_worker_token

        request = _make_request()  # no header
        settings = _settings()

        with patch(_ASYNC_MODE_PATH, return_value=True):
            with pytest.raises(HTTPException) as exc_info:
                verify_worker_token(request, settings)
        assert exc_info.value.status_code == 401

    def test_raises_401_when_header_not_bearer(self):
        """Non-Bearer Authorization header → 401."""
        from app.modules.rag.api.worker_auth import verify_worker_token

        request = _make_request("Basic dXNlcjpwYXNz")
        settings = _settings()

        with patch(_ASYNC_MODE_PATH, return_value=True):
            with pytest.raises(HTTPException) as exc_info:
                verify_worker_token(request, settings)
        assert exc_info.value.status_code == 401

    def test_raises_401_when_token_invalid(self):
        """google.oauth2.id_token raising ValueError → 401."""
        from app.modules.rag.api.worker_auth import verify_worker_token

        request = _make_request("Bearer bad-token")
        settings = _settings()

        with patch(_ASYNC_MODE_PATH, return_value=True), \
             patch(_VERIFY_PATH, side_effect=ValueError("Token expired")):
            with pytest.raises(HTTPException) as exc_info:
                verify_worker_token(request, settings)
        assert exc_info.value.status_code == 401

    def test_raises_401_when_email_mismatch(self):
        """Valid token but wrong email claim → 401."""
        from app.modules.rag.api.worker_auth import verify_worker_token

        request = _make_request("Bearer valid-token")
        settings = _settings()

        fake_id_info = {
            "email": "attacker@evil.com",
            "email_verified": True,
        }
        with patch(_ASYNC_MODE_PATH, return_value=True), \
             patch(_VERIFY_PATH, return_value=fake_id_info):
            with pytest.raises(HTTPException) as exc_info:
                verify_worker_token(request, settings)
        assert exc_info.value.status_code == 401

    def test_raises_401_when_email_not_verified(self):
        """Correct email but email_verified=False → 401."""
        from app.modules.rag.api.worker_auth import verify_worker_token

        request = _make_request("Bearer valid-token")
        settings = _settings()

        fake_id_info = {
            "email": settings.cloud_run_sa_email,
            "email_verified": False,
        }
        with patch(_ASYNC_MODE_PATH, return_value=True), \
             patch(_VERIFY_PATH, return_value=fake_id_info):
            with pytest.raises(HTTPException) as exc_info:
                verify_worker_token(request, settings)
        assert exc_info.value.status_code == 401

    def test_raises_503_when_sa_email_not_configured(self):
        """CLOUD_RUN_SA_EMAIL unset in production → 503 misconfiguration."""
        from app.modules.rag.api.worker_auth import verify_worker_token

        request = _make_request("Bearer valid-token")
        settings = _settings(cloud_run_sa_email=None)

        fake_id_info = {"email": "tasks-sa@project.iam.gserviceaccount.com", "email_verified": True}
        with patch(_ASYNC_MODE_PATH, return_value=True), \
             patch(_VERIFY_PATH, return_value=fake_id_info):
            with pytest.raises(HTTPException) as exc_info:
                verify_worker_token(request, settings)
        assert exc_info.value.status_code == 503

    def test_passes_with_valid_token_and_correct_email(self):
        """Happy path: valid token, correct email → returns None."""
        from app.modules.rag.api.worker_auth import verify_worker_token

        request = _make_request("Bearer valid-token")
        settings = _settings()

        fake_id_info = {
            "email": settings.cloud_run_sa_email,
            "email_verified": True,
        }
        mock_transport = MagicMock()
        with patch(_ASYNC_MODE_PATH, return_value=True), \
             patch(_HTTP_REQ_PATH, return_value=mock_transport), \
             patch(_VERIFY_PATH, return_value=fake_id_info) as mock_verify:
            result = verify_worker_token(request, settings)

        assert result is None
        mock_verify.assert_called_once_with(
            "valid-token",
            mock_transport,
            audience="https://dms-backend.run.app",
        )


def unittest_any_transport():
    """Matcher that accepts any argument (used for the transport object)."""
    class _Any:
        def __eq__(self, other):
            return True
    return _Any()
