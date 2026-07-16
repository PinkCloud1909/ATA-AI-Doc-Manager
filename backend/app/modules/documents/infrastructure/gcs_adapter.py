import uuid
from datetime import datetime, timedelta
from typing import Any

from google.cloud import storage

from app.core.config import Settings, get_settings
from app.core.exceptions import ValidationError
from app.shared.utils import safe_filename


class GcsAdapter:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.bucket_name = self.settings.gcs_bucket
        self.client = storage.Client(project=self.settings.gcp_project_id)

    def upload_file(
        self,
        file_path: str,
        object_key: str,
        content_type: str | None = None,
    ) -> str:
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(object_key)
        blob.upload_from_filename(file_path, content_type=content_type)
        return self._build_reference(bucket_name=self.bucket_name, object_key=object_key)

    def get_object_info(self, object_reference: str) -> Any:
        bucket_name, object_key = self._parse_reference(object_reference)
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(object_key)
        blob.reload()
        return blob

    def generate_signed_download_url(
        self,
        object_reference: str,
        expires: timedelta | None = None,
    ) -> str:
        bucket_name, object_key = self._parse_reference(object_reference)
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(object_key)
        ttl = expires or timedelta(minutes=self.settings.gcs_signed_url_expiry_minutes)
        return blob.generate_signed_url(expiration=ttl, method="GET")

    def delete_object(self, object_reference: str) -> None:
        bucket_name, object_key = self._parse_reference(object_reference)
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(object_key)
        blob.delete()

    def build_object_key(self, filename: str, prefix: str = "documents") -> str:
        safe_name = safe_filename(filename)
        dated_prefix = datetime.utcnow().strftime("%Y/%m/%d")
        normalized_prefix = prefix.strip("/")
        return f"{normalized_prefix}/{dated_prefix}/{uuid.uuid4().hex}-{safe_name}"

    def _build_reference(self, bucket_name: str, object_key: str) -> str:
        return f"gcs://{bucket_name}/{object_key}"

    def _parse_reference(self, object_reference: str) -> tuple[str, str]:
        value = object_reference.removeprefix("gcs://")
        bucket_name, separator, object_key = value.partition("/")
        if not separator or not bucket_name or not object_key:
            raise ValidationError("Invalid GCS object reference")
        return bucket_name, object_key
