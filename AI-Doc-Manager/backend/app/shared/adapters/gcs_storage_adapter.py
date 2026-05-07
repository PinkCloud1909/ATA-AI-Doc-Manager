import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from google.cloud import storage

from app.core.config import Settings, get_settings
from app.core.exceptions import ValidationError
from app.shared.interfaces import IObjectStorage
from app.shared.utils import safe_filename


class GCSStorageAdapter(IObjectStorage):
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.bucket_name = self.settings.gcs_bucket_name
        self.client = storage.Client(project=self.settings.gcp_project_id)
        self.bucket = self.client.bucket(self.bucket_name)

    def ensure_bucket(self) -> None:
        if not self.bucket.exists():
            self.bucket.create(location=self.settings.gcp_location or "US")

    def upload_file(self, file_path: str, object_key: str, content_type: Optional[str] = None) -> str:
        blob = self.bucket.blob(object_key)
        blob.upload_from_filename(file_path, content_type=content_type)
        return self._build_reference(bucket_name=self.bucket_name, object_key=object_key)

    def upload_fileobj(self, file_obj: Any, object_key: str, content_type: Optional[str] = None, length: int = -1) -> str:
        blob = self.bucket.blob(object_key)
        blob.upload_from_file(file_obj, content_type=content_type or "application/octet-stream")
        return self._build_reference(bucket_name=self.bucket_name, object_key=object_key)

    def get_object_info(self, object_reference: str) -> Any:
        bucket_name, object_key = self._parse_reference(object_reference)
        blob = self.client.bucket(bucket_name).get_blob(object_key)
        return blob

    def generate_presigned_download_url(self, object_reference: str, expires: Optional[timedelta] = None) -> str:
        bucket_name, object_key = self._parse_reference(object_reference)
        blob = self.client.bucket(bucket_name).blob(object_key)
        ttl = expires or timedelta(minutes=self.settings.minio_presigned_expiry_minutes)
        return blob.generate_signed_url(version="v4", expiration=ttl, method="GET")

    def delete_object(self, object_reference: str) -> None:
        bucket_name, object_key = self._parse_reference(object_reference)
        blob = self.client.bucket(bucket_name).blob(object_key)
        if blob.exists():
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
