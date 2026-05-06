"""
services/gcs_service.py
Wrapper cho Google Cloud Storage.
- fetch_document_text(): đọc nội dung text từ docx/pdf để đưa vào RAG prompt
- generate_signed_url():  tạo Signed URL để FE download
"""
from __future__ import annotations

import io
import structlog
from datetime import timedelta
from tenacity import retry, stop_after_attempt, wait_exponential

from google.cloud import storage

from app.core.config import settings

logger = structlog.get_logger()

_client: storage.Client | None = None


def _get_client() -> storage.Client:
    global _client
    if _client is None:
        _client = storage.Client(project=settings.GCP_PROJECT_ID)
    return _client


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
async def fetch_document_text(gcs_path: str) -> str:
    """
    Tải file từ GCS và extract text.
    gcs_path format: "bucket-name/path/to/file.pdf" hoặc "path/to/file.pdf"

    Hỗ trợ: .pdf (pdfminer), .docx (python-docx), .txt
    """
    # Parse bucket và blob path
    if gcs_path.startswith("gs://"):
        gcs_path = gcs_path[5:]
    parts = gcs_path.split("/", 1)
    bucket_name = parts[0] if len(parts) == 2 and "." not in parts[0][:20] else settings.GCS_BUCKET_NAME
    blob_name   = parts[1] if len(parts) == 2 and "." not in parts[0][:20] else gcs_path

    logger.info("gcs_fetch_start", bucket=bucket_name, blob=blob_name)

    client = _get_client()
    bucket = client.bucket(bucket_name)
    blob   = bucket.blob(blob_name)

    file_bytes = blob.download_as_bytes()
    filename   = blob_name.lower()

    text = _extract_text(file_bytes, filename)
    logger.info("gcs_fetch_done", chars=len(text))
    return text


def _extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract plain text từ file bytes dựa vào extension."""

    if filename.endswith(".pdf"):
        try:
            from pdfminer.high_level import extract_text_to_fp
            from pdfminer.layout import LAParams
            output = io.StringIO()
            extract_text_to_fp(io.BytesIO(file_bytes), output, laparams=LAParams())
            return output.getvalue()
        except ImportError:
            logger.warning("pdfminer not installed, returning empty text for PDF")
            return ""

    elif filename.endswith((".docx", ".doc")):
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            logger.warning("python-docx not installed")
            return ""

    elif filename.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")

    else:
        # Cố gắng decode as UTF-8
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return ""


def generate_signed_download_url(gcs_path: str, ttl_seconds: int | None = None) -> str:
    """
    Tạo V4 Signed URL để FE download file.
    TTL mặc định: 15 phút (GCS_SIGNED_URL_TTL trong config).
    """
    ttl = ttl_seconds or settings.GCS_SIGNED_URL_TTL

    if gcs_path.startswith("gs://"):
        gcs_path = gcs_path[5:]
    parts = gcs_path.split("/", 1)
    bucket_name = parts[0] if len(parts) == 2 and "." not in parts[0][:20] else settings.GCS_BUCKET_NAME
    blob_name   = parts[1] if len(parts) == 2 and "." not in parts[0][:20] else gcs_path

    client  = _get_client()
    bucket  = client.bucket(bucket_name)
    blob    = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(seconds=ttl),
        method="GET",
    )
    return url
