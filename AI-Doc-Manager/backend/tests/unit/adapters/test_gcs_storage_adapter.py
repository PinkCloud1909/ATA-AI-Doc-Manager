"""Unit tests for GCSStorageAdapter.

All ``google.cloud.storage`` calls are mocked so these tests run offline
without any GCP credentials or network access.

Coverage
--------
- ``__init__`` — client creation with correct project
- ``ensure_bucket`` — creates when absent, skips when exists, handles 403 gracefully
- ``upload_file`` / ``upload_fileobj`` — happy path, reference format
- ``get_object_info`` — returns Blob, raises NotFoundError
- ``delete_object`` — deletes, silently handles missing, raises on Forbidden
- ``generate_presigned_download_url`` — v4 URLs, response_disposition, error paths
- ``build_object_key`` — correct date-prefixed format
- ``_parse_reference`` / ``_build_reference`` — parsing and construction
- Retry logic — retries on transient errors, fast-fails on permanent errors
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import ExternalServiceError, NotFoundError, ValidationError

# ---------------------------------------------------------------------------
# Paths patched in the adapter module
# ---------------------------------------------------------------------------
_STORAGE_CLIENT_PATH = "app.shared.adapters.gcs_storage_adapter.storage.Client"
_AUTH_DEFAULT_PATH = "google.auth.default"
_AUTH_REQUEST_PATH = "google.auth.transport.requests.Request"
_TIME_SLEEP_PATH = "app.shared.adapters.gcs_storage_adapter.time.sleep"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_settings(**overrides) -> SimpleNamespace:
    """Minimal Settings stand-in for the GCS adapter."""
    defaults: dict = {
        "gcs_bucket_name": "test-bucket",
        "gcp_project_id": "test-project",
        "gcp_location": "us-central1",
        "gcs_presigned_expiry_minutes": 15,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.fixture()
def mock_storage_client():
    """Patch ``google.cloud.storage.Client``."""
    with patch(_STORAGE_CLIENT_PATH) as mock_client_cls:
        mock_client = MagicMock(name="StorageClient")
        mock_bucket = MagicMock(name="Bucket")
        mock_client.bucket.return_value = mock_bucket
        mock_client_cls.return_value = mock_client
        yield mock_client_cls, mock_client, mock_bucket


@pytest.fixture()
def gcs(mock_storage_client):
    """Return a GCSStorageAdapter with mocked GCS client."""
    from app.shared.adapters.gcs_storage_adapter import GCSStorageAdapter

    mock_cls, mock_client, mock_bucket = mock_storage_client
    settings = _make_settings()
    adapter = GCSStorageAdapter(settings=settings)
    adapter._mock_client = mock_client
    adapter._mock_bucket = mock_bucket
    return adapter


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


class TestInit:
    def test_creates_client_with_project(self, mock_storage_client):
        mock_cls, _, _ = mock_storage_client
        settings = _make_settings(gcp_project_id="my-proj-123")
        from app.shared.adapters.gcs_storage_adapter import GCSStorageAdapter

        GCSStorageAdapter(settings=settings)

        mock_cls.assert_called_once_with(project="my-proj-123")

    def test_uses_default_settings_when_none_provided(self, mock_storage_client):
        mock_cls, _, _ = mock_storage_client
        from app.shared.adapters.gcs_storage_adapter import GCSStorageAdapter

        adapter = GCSStorageAdapter()
        assert adapter.settings is not None
        assert adapter.bucket_name is not None


# ---------------------------------------------------------------------------
# Bucket management
# ---------------------------------------------------------------------------


class TestEnsureBucket:
    def test_skips_when_bucket_exists(self, gcs):
        gcs._mock_bucket.exists.return_value = True

        gcs.ensure_bucket()

        gcs._mock_bucket.create.assert_not_called()

    def test_creates_when_bucket_absent(self, gcs):
        gcs._mock_bucket.exists.return_value = False

        gcs.ensure_bucket()

        gcs._mock_bucket.create.assert_called_once_with(location="us-central1")

    def test_handles_forbidden_on_exists_check(self, gcs):
        from google.api_core import exceptions as gcp_exceptions

        gcs._mock_bucket.exists.side_effect = gcp_exceptions.Forbidden("no access")
        gcs._mock_bucket.create.return_value = None  # succeeds

        gcs.ensure_bucket()

        gcs._mock_bucket.create.assert_called_once()

    def test_handles_conflict_on_create(self, gcs):
        from google.api_core import exceptions as gcp_exceptions

        gcs._mock_bucket.exists.return_value = False
        gcs._mock_bucket.create.side_effect = gcp_exceptions.Conflict(
            "already exists"
        )

        # Should not raise
        gcs.ensure_bucket()

    def test_raises_external_service_error_on_create_forbidden(self, gcs):
        from google.api_core import exceptions as gcp_exceptions

        gcs._mock_bucket.exists.return_value = False
        gcs._mock_bucket.create.side_effect = gcp_exceptions.Forbidden(
            "permission denied"
        )

        with pytest.raises(ExternalServiceError, match="Permission denied"):
            gcs.ensure_bucket()


# ---------------------------------------------------------------------------
# Uploads
# ---------------------------------------------------------------------------


class TestUploadFile:
    def test_uploads_and_returns_reference(self, gcs):
        blob = MagicMock()
        blob.size = 12345
        gcs._mock_bucket.blob.return_value = blob

        ref = gcs.upload_file("/tmp/doc.pdf", "documents/2026/07/abc.pdf")

        blob.upload_from_filename.assert_called_once_with(
            "/tmp/doc.pdf", content_type=None
        )
        assert ref == "gcs://test-bucket/documents/2026/07/abc.pdf"

    def test_uploads_with_content_type(self, gcs):
        blob = MagicMock()
        blob.size = 100
        gcs._mock_bucket.blob.return_value = blob

        gcs.upload_file("/tmp/doc.pdf", "key", content_type="application/pdf")

        blob.upload_from_filename.assert_called_once_with(
            "/tmp/doc.pdf", content_type="application/pdf"
        )


class TestUploadFileobj:
    def test_uploads_with_default_content_type(self, gcs):
        blob = MagicMock()
        blob.size = 50
        gcs._mock_bucket.blob.return_value = blob
        file_obj = MagicMock()

        ref = gcs.upload_fileobj(file_obj, "key")

        blob.upload_from_file.assert_called_once_with(
            file_obj, content_type="application/octet-stream"
        )
        assert ref.startswith("gcs://test-bucket/")

    def test_uploads_with_custom_content_type(self, gcs):
        blob = MagicMock()
        gcs._mock_bucket.blob.return_value = blob
        file_obj = MagicMock()

        gcs.upload_fileobj(file_obj, "key", content_type="image/png")

        call_kwargs = blob.upload_from_file.call_args.kwargs
        assert call_kwargs["content_type"] == "image/png"

    def test_passes_size_when_length_known(self, gcs):
        blob = MagicMock()
        gcs._mock_bucket.blob.return_value = blob
        file_obj = MagicMock()

        gcs.upload_fileobj(file_obj, "key", length=1048576)

        call_kwargs = blob.upload_from_file.call_args.kwargs
        assert call_kwargs["size"] == 1048576

    def test_omits_size_when_length_unknown(self, gcs):
        blob = MagicMock()
        gcs._mock_bucket.blob.return_value = blob
        file_obj = MagicMock()

        gcs.upload_fileobj(file_obj, "key", length=-1)

        call_kwargs = blob.upload_from_file.call_args.kwargs
        assert "size" not in call_kwargs


# ---------------------------------------------------------------------------
# Object info
# ---------------------------------------------------------------------------


class TestGetObjectInfo:
    def test_returns_blob(self, gcs):
        blob = MagicMock(name="Blob")
        gcs._mock_bucket.get_blob.return_value = blob

        result = gcs.get_object_info("gcs://test-bucket/my/key.txt")

        assert result is blob
        gcs._mock_bucket.get_blob.assert_called_once_with("my/key.txt")

    def test_raises_not_found_when_blob_is_none(self, gcs):
        gcs._mock_bucket.get_blob.return_value = None

        with pytest.raises(NotFoundError, match="GCS object not found"):
            gcs.get_object_info("gcs://test-bucket/my/key.txt")


# ---------------------------------------------------------------------------
# Deletion
# ---------------------------------------------------------------------------


class TestDeleteObject:
    def test_deletes_blob(self, gcs):
        blob = MagicMock()
        gcs._mock_bucket.blob.return_value = blob

        gcs.delete_object("gcs://test-bucket/my/key.txt")

        blob.delete.assert_called_once()

    def test_silently_handles_missing_object(self, gcs):
        from google.api_core import exceptions as gcp_exceptions

        blob = MagicMock()
        blob.delete.side_effect = gcp_exceptions.NotFound("not there")
        gcs._mock_bucket.blob.return_value = blob

        # Should not raise
        gcs.delete_object("gcs://test-bucket/my/key.txt")

    def test_raises_on_forbidden(self, gcs):
        from google.api_core import exceptions as gcp_exceptions

        blob = MagicMock()
        blob.delete.side_effect = gcp_exceptions.Forbidden("no access")
        gcs._mock_bucket.blob.return_value = blob

        with pytest.raises(ExternalServiceError, match="Permission denied"):
            gcs.delete_object("gcs://test-bucket/my/key.txt")


# ---------------------------------------------------------------------------
# Presigned URLs
# ---------------------------------------------------------------------------


class TestGeneratePresignedDownloadUrl:
    @pytest.fixture(autouse=True)
    def _mock_auth(self):
        """Suppress real google.auth calls inside _get_signing_credentials."""
        with patch(_AUTH_DEFAULT_PATH) as mock_default, patch(
            _AUTH_REQUEST_PATH
        ) as mock_req_cls:
            mock_creds = MagicMock(name="Credentials")
            mock_default.return_value = (mock_creds, "test-project")
            mock_req_cls.return_value = MagicMock(name="Request")
            yield mock_default, mock_creds

    def test_generates_v4_get_url(self, gcs):
        blob = MagicMock()
        blob.generate_signed_url.return_value = "https://storage.googleapis.com/..."
        gcs._mock_bucket.blob.return_value = blob

        url = gcs.generate_presigned_download_url("gcs://test-bucket/my/key.txt")

        assert url == "https://storage.googleapis.com/..."
        call_kwargs = blob.generate_signed_url.call_args.kwargs
        assert call_kwargs["version"] == "v4"
        assert call_kwargs["method"] == "GET"
        assert call_kwargs["credentials"] is not None

    def test_uses_custom_expiry(self, gcs):
        blob = MagicMock()
        blob.generate_signed_url.return_value = "https://example.com/signed"
        gcs._mock_bucket.blob.return_value = blob

        gcs.generate_presigned_download_url(
            "gcs://test-bucket/my/key.txt",
            expires=timedelta(hours=1),
        )

        call_kwargs = blob.generate_signed_url.call_args.kwargs
        assert call_kwargs["expiration"] == timedelta(hours=1)

    def test_default_expiry_from_settings(self, gcs):
        blob = MagicMock()
        blob.generate_signed_url.return_value = "https://example.com/signed"
        gcs._mock_bucket.blob.return_value = blob

        gcs.generate_presigned_download_url("gcs://test-bucket/my/key.txt")

        call_kwargs = blob.generate_signed_url.call_args.kwargs
        assert call_kwargs["expiration"] == timedelta(minutes=15)

    def test_adds_response_disposition(self, gcs):
        blob = MagicMock()
        blob.generate_signed_url.return_value = "https://example.com/signed"
        gcs._mock_bucket.blob.return_value = blob

        gcs.generate_presigned_download_url(
            "gcs://test-bucket/my/key.txt",
            response_disposition="attachment; filename=report.pdf",
        )

        call_kwargs = blob.generate_signed_url.call_args.kwargs
        assert (
            call_kwargs["response_disposition"]
            == "attachment; filename=report.pdf"
        )

    def test_adds_content_type_override(self, gcs):
        blob = MagicMock()
        blob.generate_signed_url.return_value = "https://example.com/signed"
        gcs._mock_bucket.blob.return_value = blob

        gcs.generate_presigned_download_url(
            "gcs://test-bucket/my/key.txt",
            content_type="text/html",
        )

        call_kwargs = blob.generate_signed_url.call_args.kwargs
        assert call_kwargs["response_type"] == "text/html"

    def test_raises_external_service_error_on_attribute_error(self, gcs):
        blob = MagicMock()
        blob.generate_signed_url.side_effect = AttributeError(
            "'Credentials' object has no attribute 'sign_blob'"
        )
        gcs._mock_bucket.blob.return_value = blob

        with pytest.raises(
            ExternalServiceError, match="Cannot sign GCS URLs"
        ):
            gcs.generate_presigned_download_url("gcs://test-bucket/my/key.txt")

    def test_raises_external_service_error_on_generic_error(self, gcs):
        blob = MagicMock()
        blob.generate_signed_url.side_effect = RuntimeError("unexpected")
        gcs._mock_bucket.blob.return_value = blob

        with pytest.raises(
            ExternalServiceError, match="Failed to generate signed URL"
        ):
            gcs.generate_presigned_download_url("gcs://test-bucket/my/key.txt")


# ---------------------------------------------------------------------------
# Object-key builder
# ---------------------------------------------------------------------------


class TestBuildObjectKey:
    def test_produces_date_prefixed_key(self, gcs):
        key = gcs.build_object_key("report.pdf", prefix="documents")

        # Format: documents/YYYY/MM/DD/<uuid_hex>-report.pdf
        parts = key.split("/")
        assert parts[0] == "documents"
        assert len(parts[1]) == 4  # year
        assert len(parts[2]) == 2  # month
        assert len(parts[3]) == 2  # day
        filename_part = parts[4]
        assert filename_part.endswith("-report.pdf")
        uuid_hex = filename_part[:-len("-report.pdf")]
        # Must be a valid 32-char hex string
        uuid.UUID(hex=uuid_hex)

    def test_sanitizes_dangerous_filename(self, gcs):
        key = gcs.build_object_key("../../../etc/passwd", prefix="uploads")
        assert ".." not in key
        assert key.startswith("uploads/")

    def test_strips_prefix_slashes(self, gcs):
        key = gcs.build_object_key("doc.pdf", prefix="/leading/slash/")
        assert not key.startswith("/")
        assert key.startswith("leading/slash/")


# ---------------------------------------------------------------------------
# Reference parsing and building
# ---------------------------------------------------------------------------


class TestBuildReference:
    def test_builds_standard_format(self, gcs):
        ref = gcs._build_reference("path/to/object.pdf")
        assert ref == "gcs://test-bucket/path/to/object.pdf"


class TestParseReference:
    def test_parses_valid_reference(self, gcs):
        bucket, key = gcs._parse_reference("gcs://my-bucket/path/to/obj.pdf")
        assert bucket == "my-bucket"
        assert key == "path/to/obj.pdf"

    def test_parses_with_nested_path(self, gcs):
        bucket, key = gcs._parse_reference(
            "gcs://b/docs/2026/07/03/report.pdf"
        )
        assert bucket == "b"
        assert key == "docs/2026/07/03/report.pdf"

    def test_raises_on_empty_reference(self, gcs):
        with pytest.raises(ValidationError, match="Invalid GCS object reference"):
            gcs._parse_reference("")

    def test_raises_on_bare_gcs_prefix(self, gcs):
        with pytest.raises(ValidationError, match="Invalid GCS object reference"):
            gcs._parse_reference("gcs://")

    def test_raises_on_missing_key(self, gcs):
        with pytest.raises(ValidationError, match="Invalid GCS object reference"):
            gcs._parse_reference("gcs://my-bucket/")

    def test_raises_on_missing_bucket(self, gcs):
        with pytest.raises(ValidationError, match="Invalid GCS object reference"):
            gcs._parse_reference("gcs:///key")


# ---------------------------------------------------------------------------
# Retry logic
# ---------------------------------------------------------------------------


class TestRetryOnTransient:
    """Verify the _retry_on_transient decorator behaviour."""

    def test_retries_on_service_unavailable_delete(self, gcs):
        from google.api_core import exceptions as gcp_exceptions

        blob = MagicMock()
        blob.delete.side_effect = [
            gcp_exceptions.ServiceUnavailable("try again"),
            gcp_exceptions.ServiceUnavailable("try again"),
            None,
        ]
        gcs._mock_bucket.blob.return_value = blob

        with patch(_TIME_SLEEP_PATH) as mock_sleep:
            gcs.delete_object("gcs://test-bucket/key")

        assert mock_sleep.call_count == 2

    def test_retries_on_too_many_requests_delete(self, gcs):
        from google.api_core import exceptions as gcp_exceptions

        blob = MagicMock()
        blob.delete.side_effect = [
            gcp_exceptions.TooManyRequests("slow down"),
            None,
        ]
        gcs._mock_bucket.blob.return_value = blob

        with patch(_TIME_SLEEP_PATH):
            gcs.delete_object("gcs://test-bucket/key")

    def test_fast_fails_on_not_found_delete(self, gcs):
        from google.api_core import exceptions as gcp_exceptions

        blob = MagicMock()
        blob.delete.side_effect = gcp_exceptions.NotFound("gone")
        gcs._mock_bucket.blob.return_value = blob

        with patch(_TIME_SLEEP_PATH) as mock_sleep:
            # NotFound is handled silently by delete_object
            gcs.delete_object("gcs://test-bucket/key")

        mock_sleep.assert_not_called()

    def test_fast_fails_on_forbidden(self, gcs):
        from google.api_core import exceptions as gcp_exceptions

        blob = MagicMock()
        blob.delete.side_effect = gcp_exceptions.Forbidden("no access")
        gcs._mock_bucket.blob.return_value = blob

        with patch(_TIME_SLEEP_PATH) as mock_sleep:
            with pytest.raises(ExternalServiceError):
                gcs.delete_object("gcs://test-bucket/key")

        mock_sleep.assert_not_called()

    def test_exhausts_retries_then_raises(self, gcs):
        from google.api_core import exceptions as gcp_exceptions

        blob = MagicMock()
        blob.delete.side_effect = gcp_exceptions.ServiceUnavailable(
            "always down"
        )
        gcs._mock_bucket.blob.return_value = blob

        with patch(_TIME_SLEEP_PATH) as mock_sleep:
            with pytest.raises(gcp_exceptions.ServiceUnavailable):
                gcs.delete_object("gcs://test-bucket/key")

        # 3 attempts = 0, 1, 2 → sleeps on attempts 0 and 1, then raises.
        assert mock_sleep.call_count == 2
