"""Google Cloud Storage adapter implementing the ``IObjectStorage`` port.

Used in **every environment** — local development authenticates via
Application Default Credentials (``gcloud auth application-default login``),
production via the attached service account.  Uses ``google-cloud-storage``.

Features
--------
- Simple uploads (< 8 MiB) and resumable uploads (> 8 MiB, automatic).
- V4 signed download URLs via IAM signBlob (ADC-based — no private key file
  needed in Cloud Run as long as the attached service account has
  ``roles/iam.serviceAccountTokenCreator`` on itself).
- Exponential-backoff retries on transient errors (429, 500, 502, 503).
- ``NotFoundError`` raised when an object is missing.
- Thread-safe — the underlying ``storage.Client`` is safe for concurrent use.

Required IAM for the Cloud Run service account
----------------------------------------------
+--------------------------------------+-------------------------------------+
| Permission / Role                    | Purpose                             |
+======================================+=====================================+
| ``roles/storage.objectUser``         | Upload, download, delete objects    |
+--------------------------------------+-------------------------------------+
| ``roles/storage.objectCreator``      | Minimum for upload-only workloads   |
| (alternative to objectUser)          |                                     |
+--------------------------------------+-------------------------------------+
| ``roles/iam.serviceAccountTokenCreator``| Sign V4 URLs (grant the SA this   |
| on the SA itself                     | role ON ITSELF)                     |
+--------------------------------------+-------------------------------------+
| ``roles/storage.admin``              | Create bucket (one-time setup)      |
| (or bucket-level ``storage.legacyBucketOwner``) |                       |
+--------------------------------------+-------------------------------------+
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from google.api_core import exceptions as gcp_exceptions
from google.cloud import storage

from app.core.config import Settings, get_settings
from app.core.exceptions import ExternalServiceError, NotFoundError, ValidationError
from app.shared.interfaces import IObjectStorage
from app.shared.utils import safe_filename

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Retry configuration for transient GCS errors
# ---------------------------------------------------------------------------
_RETRYABLE_STATUSES = frozenset({429, 500, 502, 503})
_MAX_RETRY_ATTEMPTS = 3
_RETRY_BASE_DELAY_SECONDS = 1.0  # doubles each attempt: 1, 2, 4 s


def _is_retryable(exception: Exception) -> bool:
    """Return ``True`` when the exception is a transient GCS / network error."""
    if isinstance(exception, gcp_exceptions.ServiceUnavailable):
        return True  # 503
    if isinstance(exception, gcp_exceptions.TooManyRequests):
        return True  # 429
    if isinstance(exception, gcp_exceptions.InternalServerError):
        return True  # 500
    if isinstance(exception, gcp_exceptions.BadGateway):
        return True  # 502
    if isinstance(exception, ConnectionError):
        return True
    if isinstance(exception, TimeoutError):
        return True
    # google.api_core.exceptions.ServerError is a base for 5xx; check the code.
    if isinstance(exception, gcp_exceptions.ServerError):
        code = getattr(exception, "code", None)
        return code in _RETRYABLE_STATUSES if code is not None else True
    return False


def _retry_on_transient(func: Any) -> Any:
    """Decorator: retry *func* with exponential backoff on transient errors."""

    def wrapper(self: "GCSStorageAdapter", *args: Any, **kwargs: Any) -> Any:
        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRY_ATTEMPTS):
            try:
                return func(self, *args, **kwargs)
            except Exception as exc:
                last_exc = exc
                if not _is_retryable(exc) or attempt == _MAX_RETRY_ATTEMPTS - 1:
                    raise
                delay = _RETRY_BASE_DELAY_SECONDS * (2**attempt)
                logger.warning(
                    "gcs_retry_transient",
                    extra={
                        "attempt": attempt + 1,
                        "max_attempts": _MAX_RETRY_ATTEMPTS,
                        "delay_s": delay,
                        "error": str(exc),
                    },
                )
                time.sleep(delay)
        # Should never be reached, but placate type checkers.
        raise last_exc  # type: ignore[misc]

    return wrapper


class GCSStorageAdapter(IObjectStorage):
    """Google Cloud Storage implementation of ``IObjectStorage``.

    Thread-safe.  Create **one** instance via ``factory.get_object_storage()``
    and reuse it for the process lifetime — the underlying ``storage.Client``
    manages its own connection pool.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.bucket_name = self.settings.gcs_bucket_name
        self.client = storage.Client(project=self.settings.gcp_project_id)
        self.bucket = self.client.bucket(self.bucket_name)

    # ------------------------------------------------------------------
    # Bucket management
    # ------------------------------------------------------------------

    def ensure_bucket(self) -> None:
        """Create the bucket if it does not already exist.

        Attempts a lightweight existence check first.  If the service account
        lacks ``storage.buckets.get`` (e.g. only ``storage.objectUser`` is
        granted) the check returns 403 — in that case we fall back to
        attempting creation and silently ignore the 409 Conflict (bucket
        already exists, owned by another project).
        """
        try:
            if self.bucket.exists():
                return
        except gcp_exceptions.Forbidden:
            logger.info(
                "gcs_bucket_exists_forbidden",
                extra={
                    "bucket": self.bucket_name,
                    "detail": (
                        "The service account lacks storage.buckets.get on this "
                        "bucket.  Attempting create as fallback — if the bucket "
                        "already exists this will result in a 409 Conflict "
                        "which is handled silently."
                    ),
                },
            )
        except gcp_exceptions.GoogleAPICallError as exc:
            logger.warning(
                "gcs_bucket_exists_failed",
                extra={"bucket": self.bucket_name, "error": str(exc)},
            )
            # Proceed to create attempt — it may succeed.

        self._create_bucket()

    @_retry_on_transient
    def _create_bucket(self) -> None:
        try:
            self.bucket.create(location=self.settings.gcp_location or "US")
            logger.info(
                "gcs_bucket_created",
                extra={
                    "bucket": self.bucket_name,
                    "location": self.settings.gcp_location or "US",
                },
            )
        except gcp_exceptions.Conflict:
            logger.info(
                "gcs_bucket_already_exists",
                extra={"bucket": self.bucket_name},
            )
        except gcp_exceptions.Forbidden as exc:
            raise ExternalServiceError(
                f"Permission denied creating GCS bucket '{self.bucket_name}'. "
                f"Grant the service account roles/storage.admin on the project "
                f"or have an administrator create the bucket.  Detail: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Uploads
    # ------------------------------------------------------------------

    @_retry_on_transient
    def upload_file(
        self, file_path: str, object_key: str, content_type: str | None = None
    ) -> str:
        """Upload a file from a local path.

        For files < 8 MiB this performs a simple (single-request) upload.
        For larger files the client automatically switches to a resumable
        upload with 100 MiB chunks.
        """
        blob = self.bucket.blob(object_key)
        blob.upload_from_filename(file_path, content_type=content_type)
        logger.debug(
            "gcs_upload_file",
            extra={"object_key": object_key, "size": blob.size},
        )
        return self._build_reference(object_key)

    @_retry_on_transient
    def upload_fileobj(
        self,
        file_obj: Any,
        object_key: str,
        content_type: str | None = None,
        length: int = -1,
    ) -> str:
        """Upload from a file-like object.

        When *length* is known (>= 0) it is forwarded to the GCS client as
        the ``size`` hint, which enables resumable-upload chunking without
        buffering the entire stream in memory.
        """
        blob = self.bucket.blob(object_key)
        kwargs: dict[str, Any] = {
            "content_type": content_type or "application/octet-stream",
        }
        if length >= 0:
            kwargs["size"] = length
        blob.upload_from_file(file_obj, **kwargs)
        logger.debug(
            "gcs_upload_fileobj",
            extra={"object_key": object_key, "size": blob.size},
        )
        return self._build_reference(object_key)

    # ------------------------------------------------------------------
    # Object info
    # ------------------------------------------------------------------

    def get_object_info(self, object_reference: str) -> storage.Blob:
        """Return the GCS Blob for *object_reference*.

        Raises ``NotFoundError`` when the object does not exist.
        """
        _, object_key = self._parse_reference(object_reference)
        blob = self.bucket.get_blob(object_key)
        if blob is None:
            raise NotFoundError(
                f"GCS object not found: {object_key}"
            )
        return blob

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    @_retry_on_transient
    def delete_object(self, object_reference: str) -> None:
        """Delete an object.  No error if the object is already absent.

        Uses a direct delete call (no ``exists()`` pre-check) to avoid a
        TOCTOU race condition between the check and the delete.
        """
        _, object_key = self._parse_reference(object_reference)
        blob = self.bucket.blob(object_key)
        try:
            blob.delete()
            logger.debug("gcs_delete_object", extra={"object_key": object_key})
        except gcp_exceptions.NotFound:
            logger.debug(
                "gcs_delete_object_not_found",
                extra={"object_key": object_key},
            )
        except gcp_exceptions.Forbidden as exc:
            raise ExternalServiceError(
                f"Permission denied deleting GCS object '{object_key}'. "
                f"Detail: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Presigned URLs
    # ------------------------------------------------------------------

    def generate_presigned_download_url(
        self,
        object_reference: str,
        expires: timedelta | None = None,
        *,
        response_disposition: str | None = None,
        content_type: str | None = None,
    ) -> str:
        """Generate a V4 signed URL for downloading an object (GET).

        Uses Application Default Credentials (ADC) so no service-account key
        file is required.  In Cloud Run the attached service account is used
        automatically, **provided** it holds the
        ``iam.serviceAccounts.signBlob`` permission on itself (grant
        ``roles/iam.serviceAccountTokenCreator`` to the SA on itself).

        Parameters
        ----------
        object_reference:
            Full GCS reference string (``gcs://bucket/key``).
        expires:
            URL lifetime.  Defaults to ``GCS_PRESIGNED_EXPIRY_MINUTES``.
        response_disposition:
            Optional ``Content-Disposition`` header value, e.g.
            ``"attachment; filename=report.pdf"`` to force a download dialog.
        content_type:
            Optional ``Content-Type`` override for the response.
        """
        _, object_key = self._parse_reference(object_reference)
        blob = self.bucket.blob(object_key)
        ttl = expires or timedelta(
            minutes=self.settings.gcs_presigned_expiry_minutes
        )

        # Obtain signing credentials.  google-cloud-storage's
        # generate_signed_url() can use the client's built-in credentials if
        # they implement the Signer interface (i.e. have sign_blob).  In
        # Cloud Run with ADC the credentials DO implement Signer via the IAM
        # signBlob API call, so we pass them explicitly for clarity and to
        # avoid the client trying a local private key first.
        credentials = self._get_signing_credentials()

        # Extract service_account_email and access_token from the credentials.
        # These are needed so that generate_signed_url_v4() delegates signing
        # to the IAM signBlob API instead of requiring a local private key
        # (which Compute Engine / Cloud Run default credentials lack).
        # See: google/cloud/storage/_signing.py lines 546-548
        signing_email = getattr(credentials, "service_account_email", None)
        signing_token = getattr(credentials, "token", None)

        kwargs: dict[str, Any] = {
            "version": "v4",
            "expiration": ttl,
            "method": "GET",
            "credentials": credentials,
        }
        if signing_email and signing_token:
            kwargs["service_account_email"] = signing_email
            kwargs["access_token"] = signing_token
        if response_disposition:
            kwargs["response_disposition"] = response_disposition
        if content_type:
            kwargs["response_type"] = content_type

        try:
            url = self._generate_signed_url(blob, kwargs)
        except AttributeError as exc:
            # google-cloud-storage raises AttributeError when the credential
            # object lacks a sign_blob / signer attribute, which happens when
            # ADC resolves to a user account (gcloud auth login) without a
            # service-account key file.  In Cloud Run this shouldn't happen.
            raise ExternalServiceError(
                "Cannot sign GCS URLs: the current credentials do not support "
                "signing (no private key or IAM signBlob capability).  In "
                "Cloud Run, grant roles/iam.serviceAccountTokenCreator to the "
                "service account on itself.  "
                f"Detail: {exc}"
            ) from exc
        except Exception as exc:
            raise ExternalServiceError(
                f"Failed to generate signed URL for GCS object "
                f"'{object_key}': {exc}"
            ) from exc

        logger.debug(
            "gcs_presigned_url",
            extra={
                "object_key": object_key,
                "ttl_seconds": ttl.total_seconds(),
            },
        )
        return url

    @_retry_on_transient
    def _generate_signed_url(self, blob: storage.Blob, kwargs: dict[str, Any]) -> str:
        return blob.generate_signed_url(**kwargs)

    # ------------------------------------------------------------------
    # Object-key builder
    # ------------------------------------------------------------------

    def build_object_key(self, filename: str, prefix: str = "documents") -> str:
        """Build a deterministic, unique object key.

        Format: ``{prefix}/YYYY/MM/DD/{uuid_hex}-{safe_filename}``
        """
        safe_name = safe_filename(filename)
        dated_prefix = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        normalized_prefix = prefix.strip("/")
        return f"{normalized_prefix}/{dated_prefix}/{uuid.uuid4().hex}-{safe_name}"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_signing_credentials(self) -> Any:
        """Return credentials capable of signing V4 URLs.

        Fetches fresh ADC credentials and refreshes them so the token is valid.
        In Cloud Run this uses the attached service account's IAM signBlob
        endpoint — no local private key is needed.
        """
        import google.auth
        import google.auth.transport.requests

        credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        auth_request = google.auth.transport.requests.Request()
        credentials.refresh(auth_request)
        return credentials

    def _build_reference(self, object_key: str) -> str:
        """Build a ``gcs://`` reference string from an object key."""
        return f"gcs://{self.bucket_name}/{object_key}"

    @staticmethod
    def _parse_reference(object_reference: str) -> tuple[str, str]:
        """Parse a ``gcs://bucket/key`` string into (bucket, key)."""
        value = object_reference.removeprefix("gcs://")
        bucket_name, separator, object_key = value.partition("/")
        if not separator or not bucket_name or not object_key:
            raise ValidationError(
                f"Invalid GCS object reference: '{object_reference}'. "
                f"Expected format: 'gcs://bucket-name/object-key'"
            )
        return bucket_name, object_key
