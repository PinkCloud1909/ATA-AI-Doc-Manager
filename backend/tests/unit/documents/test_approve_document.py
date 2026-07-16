"""Unit tests for approve_document_route in app/modules/documents/api/router.py."""

from uuid import UUID, uuid4
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.modules.documents.api.router import approve_document_route
from app.modules.rag.domain.enums import RagIngestionStatus
from app.shared.enums import DocumentType, Status


@pytest.fixture
def mock_document():
    doc_id = uuid4()
    group_id = uuid4()
    user_id = uuid4()
    return SimpleNamespace(
        id=doc_id,
        document_group_id=group_id,
        version=1,
        document_type=DocumentType.POLICY,
        status=Status.APPROVED,
        submitted_by=user_id,
        submitted_at=None,
        approved_by=user_id,
        approved_at=None,
        rejected_by=None,
        rejected_reason=None,
        rejected_at=None,
    )


@patch("app.modules.rag.application.services.ingest_document")
@patch("app.modules.documents.api.router.get_rag_engine")
@patch("app.modules.documents.api.router.approve_document")
@patch("app.modules.documents.api.router.is_async_mode")
@patch("app.modules.documents.api.router.get_settings")
def test_approve_document_route_local_dev(
    mock_get_settings,
    mock_is_async_mode,
    mock_approve_document,
    mock_get_rag_engine,
    mock_ingest_document,
    mock_document,
):
    mock_approve_document.return_value = (mock_document, [])
    mock_is_async_mode.return_value = False
    mock_settings = MagicMock()
    mock_get_settings.return_value = mock_settings
    mock_rag_engine = MagicMock()
    mock_get_rag_engine.return_value = mock_rag_engine
    mock_ingest_document.return_value = SimpleNamespace(
        document_id=mock_document.id,
        status=RagIngestionStatus.COMPLETED.value,
        rag_file_id="test-rag-file-1",
        processing_time_ms=12.5,
        message="ok",
    )

    doc_id = mock_document.id
    current_user = SimpleNamespace(id=uuid4())
    session = MagicMock()

    response = approve_document_route(
        document_id=doc_id,
        current_user=current_user,
        session=session,
    )

    mock_approve_document.assert_called_once_with(
        session,
        document_id=doc_id,
        user_id=current_user.id,
    )
    mock_is_async_mode.assert_called_once_with(mock_settings)
    mock_ingest_document.assert_called_once_with(
        session,
        document_id=doc_id,
        rag_engine=mock_rag_engine,
        settings=mock_settings,
    )
    assert response.document_id == doc_id
    assert response.status == Status.APPROVED


@patch("app.modules.rag.application.services.ingest_document")
@patch("app.modules.documents.api.router.get_rag_engine")
@patch("app.modules.documents.api.router.approve_document")
@patch("app.modules.documents.api.router.is_async_mode")
@patch("app.modules.documents.api.router.get_settings")
def test_approve_document_route_local_dev_ingest_failure(
    mock_get_settings,
    mock_is_async_mode,
    mock_approve_document,
    mock_get_rag_engine,
    mock_ingest_document,
    mock_document,
):
    mock_approve_document.return_value = (mock_document, [])
    mock_is_async_mode.return_value = False
    mock_settings = MagicMock()
    mock_get_settings.return_value = mock_settings
    mock_get_rag_engine.return_value = MagicMock()
    mock_ingest_document.side_effect = RuntimeError("RAG Engine unavailable")

    doc_id = mock_document.id
    current_user = SimpleNamespace(id=uuid4())
    session = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        approve_document_route(
            document_id=doc_id,
            current_user=current_user,
            session=session,
        )

    assert exc_info.value.status_code == 500
    assert "RAG Engine unavailable" in exc_info.value.detail
    assert "POST /api/v1/rag/" in exc_info.value.detail


@patch("app.modules.documents.api.router.enqueue_rag_ingestion_task")
@patch("app.modules.documents.api.router.approve_document")
@patch("app.modules.documents.api.router.is_async_mode")
@patch("app.modules.documents.api.router.get_settings")
def test_approve_document_route_prod_success(
    mock_get_settings,
    mock_is_async_mode,
    mock_approve_document,
    mock_enqueue,
    mock_document,
):
    mock_approve_document.return_value = (mock_document, [])
    mock_is_async_mode.return_value = True
    mock_settings = MagicMock()
    mock_get_settings.return_value = mock_settings

    doc_id = mock_document.id
    current_user = SimpleNamespace(id=uuid4())
    session = MagicMock()

    response = approve_document_route(
        document_id=doc_id,
        current_user=current_user,
        session=session,
    )

    mock_approve_document.assert_called_once_with(
        session,
        document_id=doc_id,
        user_id=current_user.id,
    )
    mock_is_async_mode.assert_called_once_with(mock_settings)
    mock_enqueue.assert_called_once_with(
        document_id=str(doc_id),
        force=False,
        settings=mock_settings,
    )
    assert response.document_id == doc_id
    assert response.status == Status.APPROVED


@patch("app.modules.documents.api.router.enqueue_rag_ingestion_task")
@patch("app.modules.documents.api.router.approve_document")
@patch("app.modules.documents.api.router.is_async_mode")
@patch("app.modules.documents.api.router.get_settings")
def test_approve_document_route_prod_enqueue_failure(
    mock_get_settings,
    mock_is_async_mode,
    mock_approve_document,
    mock_enqueue,
    mock_document,
):
    mock_approve_document.return_value = (mock_document, [])
    mock_is_async_mode.return_value = True
    mock_settings = MagicMock()
    mock_get_settings.return_value = mock_settings
    mock_enqueue.side_effect = RuntimeError("Connection refused")

    doc_id = mock_document.id
    current_user = SimpleNamespace(id=uuid4())
    session = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        approve_document_route(
            document_id=doc_id,
            current_user=current_user,
            session=session,
        )

    assert exc_info.value.status_code == 500
    assert "Connection refused" in exc_info.value.detail
    assert "POST /api/v1/rag/" in exc_info.value.detail

    mock_enqueue.assert_called_once_with(
        document_id=str(doc_id),
        force=False,
        settings=mock_settings,
    )
