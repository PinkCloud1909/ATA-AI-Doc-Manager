import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from minio import Minio

from app.core.config import Settings, get_settings
from app.core.exceptions import ValidationError
from app.shared.interfaces import IObjectStorage
from app.shared.utils import safe_filename


class MinioStorageAdapter(IObjectStorage):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.bucket_name = self.settings.minio_bucket
        self.client = Minio(
            endpoint=self.settings.minio_endpoint,
            access_key=self.settings.minio_access_key,
            secret_key=self.settings.minio_secret_key,
            secure=self.settings.minio_secure,
        )

        external_endpoint = self.settings.minio_external_endpoint or self.settings.minio_endpoint
        self.external_client = Minio(
            endpoint=external_endpoint,
            access_key=self.settings.minio_access_key,
            secret_key=self.settings.minio_secret_key,
            secure=self.settings.minio_secure,
            region="us-east-1",
        )

    def ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def upload_file(self, file_path: str, object_key: str, content_type: str | None = None) -> str:
        self.client.fput_object(
            bucket_name=self.bucket_name,
            object_name=object_key,
            file_path=file_path,
            content_type=content_type,
        )
        return self._build_reference(bucket_name=self.bucket_name, object_key=object_key)

    def upload_fileobj(self, file_obj: Any, object_key: str, content_type: str | None = None, length: int = -1) -> str:
        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_key,
            data=file_obj,
            length=length,
            content_type=content_type or "application/octet-stream",
            part_size=10 * 1024 * 1024,
        )
        return self._build_reference(bucket_name=self.bucket_name, object_key=object_key)

    def get_object_info(self, object_reference: str) -> Any:
        bucket_name, object_key = self._parse_reference(object_reference)
        return self.client.stat_object(bucket_name=bucket_name, object_name=object_key)

    def generate_presigned_download_url(self, object_reference: str, expires: timedelta | None = None) -> str:
        bucket_name, object_key = self._parse_reference(object_reference)
        ttl = expires or timedelta(minutes=self.settings.minio_presigned_expiry_minutes)
        return self.external_client.presigned_get_object(
            bucket_name=bucket_name,
            object_name=object_key,
            expires=ttl,
        )

    def delete_object(self, object_reference: str) -> None:
        bucket_name, object_key = self._parse_reference(object_reference)
        self.client.remove_object(bucket_name=bucket_name, object_name=object_key)

    def download_object(self, object_reference: str) -> bytes:
        bucket_name, object_key = self._parse_reference(object_reference)
        response = self.client.get_object(bucket_name=bucket_name, object_name=object_key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def build_object_key(self, filename: str, prefix: str = "documents") -> str:
        safe_name = safe_filename(filename)
        dated_prefix = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        normalized_prefix = prefix.strip("/")
        return f"{normalized_prefix}/{dated_prefix}/{uuid.uuid4().hex}-{safe_name}"

    def _build_reference(self, bucket_name: str, object_key: str) -> str:
        return f"minio://{bucket_name}/{object_key}"

    def _parse_reference(self, object_reference: str) -> tuple[str, str]:
        value = object_reference.removeprefix("minio://")
        bucket_name, separator, object_key = value.partition("/")
        if not separator or not bucket_name or not object_key:
            raise ValidationError("Invalid MinIO object reference")
        return bucket_name, object_key
