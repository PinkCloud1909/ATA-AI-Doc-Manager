from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from app.modules.documents.application.services import get_document_detail


def test_document_detail_builds_distinct_preview_and_download_urls() -> None:
    document = SimpleNamespace(
        id=uuid4(),
        file_link="gcs://bucket/documents/report.pdf",
        original_filename="Báo cáo quý.pdf",
        content_type="application/pdf",
    )
    storage = Mock()
    storage.generate_presigned_download_url.side_effect = [
        "https://storage.example/preview",
        "https://storage.example/download",
    ]

    with patch(
        "app.modules.documents.application.services.get_document_by_id",
        return_value=document,
    ):
        result, preview_url, download_url = get_document_detail(
            Mock(), document.id, storage
        )

    assert result is document
    assert preview_url.endswith("/preview")
    assert download_url.endswith("/download")
    preview_call, download_call = storage.generate_presigned_download_url.call_args_list
    assert preview_call.kwargs["response_disposition"].startswith("inline;")
    assert download_call.kwargs["response_disposition"].startswith("attachment;")
    assert preview_call.kwargs["content_type"] == "application/pdf"
