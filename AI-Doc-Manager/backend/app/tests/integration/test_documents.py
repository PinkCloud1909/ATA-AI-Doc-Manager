import io
import uuid
from contextlib import contextmanager
from unittest.mock import MagicMock


from app.main import app
from app.modules.documents.api.router import _get_storage, _get_rag_engine_dep
from app.modules.documents.domain.models import Document
from app.shared.enums import DocumentType, Status
from app.shared.utils import utcnow


MOCK_FILE_LINK = "gcs://test-bucket/documents/2026/05/01/abc123-test.pdf"
MOCK_DOWNLOAD_URL = (
    "https://storage.googleapis.com/test-bucket/documents/2026/05/01/abc123-test.pdf?presigned=1"
)


@contextmanager
def _override_storage(mock_adapter):
    """Temporarily replace the _get_storage FastAPI dependency with a mock.

    @patch cannot intercept FastAPI Depends() because Depends() captures the
    function reference at route-definition time.  Using dependency_overrides is
    the correct FastAPI-idiomatic approach.
    """
    app.dependency_overrides[_get_storage] = lambda: mock_adapter
    try:
        yield mock_adapter
    finally:
        app.dependency_overrides.pop(_get_storage, None)


@contextmanager
def _override_rag_engine(mock_adapter):
    """Temporarily replace the _get_rag_engine_dep FastAPI dependency with a mock."""
    app.dependency_overrides[_get_rag_engine_dep] = lambda: mock_adapter
    try:
        yield mock_adapter
    finally:
        app.dependency_overrides.pop(_get_rag_engine_dep, None)


def _login_admin(client) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_test_document(db_session, user_id=None) -> Document:
    """Insert a document directly into the DB for testing."""
    now = utcnow()
    doc = Document(
        document_group_id=uuid.uuid4(),
        version=1,
        document_type=DocumentType.REPORT,
        status=Status.DRAFT,
        title="Test Document",
        description="A test document",
        original_filename="test.pdf",
        file_link=MOCK_FILE_LINK,
        file_size=1024,
        content_type="application/pdf",
        created_by=user_id,
        created_at=now,
        modified_by=user_id,
        modified_date=now,
    )
    db_session.add(doc)
    db_session.commit()
    return doc


class TestUploadDocument:
    def test_upload_success(self, client, db_session):
        mock_adapter = MagicMock()
        mock_adapter.build_object_key.return_value = "documents/2026/05/01/abc-test.pdf"
        mock_adapter.upload_fileobj.return_value = MOCK_FILE_LINK

        token = _login_admin(client)
        file_data = b"fake pdf content"
        with _override_storage(mock_adapter):
            response = client.post(
                "/api/v1/documents/upload",
                headers=_auth_header(token),
                files={"file": ("test.pdf", io.BytesIO(file_data), "application/pdf")},
                data={"document_type": "report", "title": "My Report"},
            )

        assert response.status_code == 201
        payload = response.json()
        assert payload["title"] == "My Report"
        assert payload["original_filename"] == "test.pdf"
        assert payload["document_type"] == "report"
        assert payload["status"] == "draft"
        assert payload["version"] == 1
        assert payload["file_size"] == len(file_data)

    def test_upload_default_title(self, client):
        mock_adapter = MagicMock()
        mock_adapter.build_object_key.return_value = "documents/2026/05/01/abc-test.pdf"
        mock_adapter.upload_fileobj.return_value = MOCK_FILE_LINK

        token = _login_admin(client)
        with _override_storage(mock_adapter):
            response = client.post(
                "/api/v1/documents/upload",
                headers=_auth_header(token),
                files={"file": ("report.pdf", io.BytesIO(b"data"), "application/pdf")},
                data={"document_type": "report"},
            )

        assert response.status_code == 201
        assert response.json()["title"] == "report.pdf"

    def test_upload_requires_auth(self, client):
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.pdf", io.BytesIO(b"data"), "application/pdf")},
        )
        assert response.status_code == 401


class TestListDocuments:
    def test_list_empty(self, client, db_session):
        token = _login_admin(client)
        response = client.get(
            "/api/v1/documents",
            headers=_auth_header(token),
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["items"] == []
        assert payload["total"] == 0
        assert payload["page"] == 1

    def test_list_with_documents(self, client, db_session):
        _create_test_document(db_session)
        _create_test_document(db_session)

        token = _login_admin(client)
        response = client.get(
            "/api/v1/documents",
            headers=_auth_header(token),
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 2
        assert len(payload["items"]) == 2

    def test_list_filter_by_status(self, client, db_session):
        doc = _create_test_document(db_session)
        doc.status = Status.APPROVED
        db_session.commit()

        _create_test_document(db_session)  # DRAFT

        token = _login_admin(client)
        response = client.get(
            "/api/v1/documents",
            headers=_auth_header(token),
            params={"status_filter": "draft"},
        )

        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_list_pagination(self, client, db_session):
        for _ in range(5):
            _create_test_document(db_session)

        token = _login_admin(client)
        response = client.get(
            "/api/v1/documents",
            headers=_auth_header(token),
            params={"page": 1, "page_size": 2},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 5
        assert len(payload["items"]) == 2
        assert payload["page"] == 1
        assert payload["page_size"] == 2


class TestGetDocument:
    def test_get_detail(self, client, db_session):
        mock_adapter = MagicMock()
        mock_adapter.generate_presigned_download_url.return_value = MOCK_DOWNLOAD_URL

        doc = _create_test_document(db_session)
        token = _login_admin(client)
        with _override_storage(mock_adapter):
            response = client.get(
                f"/api/v1/documents/{doc.id}",
                headers=_auth_header(token),
            )

        assert response.status_code == 200
        payload = response.json()
        assert payload["document_id"] == str(doc.id)
        assert payload["title"] == "Test Document"
        assert payload["download_url"] == MOCK_DOWNLOAD_URL

    def test_get_not_found(self, client, db_session):
        token = _login_admin(client)
        response = client.get(
            f"/api/v1/documents/{uuid.uuid4()}",
            headers=_auth_header(token),
        )
        assert response.status_code == 404


class TestUpdateDocument:
    def test_update_metadata(self, client, db_session):
        doc = _create_test_document(db_session)
        token = _login_admin(client)
        response = client.put(
            f"/api/v1/documents/{doc.id}",
            headers=_auth_header(token),
            json={"title": "Updated Title", "document_type": "policy"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["title"] == "Updated Title"
        assert payload["document_type"] == "policy"

    def test_update_non_draft_fails(self, client, db_session):
        doc = _create_test_document(db_session)
        doc.status = Status.APPROVED
        db_session.commit()

        token = _login_admin(client)
        response = client.put(
            f"/api/v1/documents/{doc.id}",
            headers=_auth_header(token),
            json={"title": "Should Fail"},
        )

        assert response.status_code == 409


class TestSoftDeleteDocument:
    def test_archive_document(self, client, db_session):
        doc = _create_test_document(db_session)
        token = _login_admin(client)
        response = client.delete(
            f"/api/v1/documents/{doc.id}",
            headers=_auth_header(token),
        )

        assert response.status_code == 200
        assert response.json()["detail"] == "Document archived successfully"

    def test_archive_already_archived(self, client, db_session):
        doc = _create_test_document(db_session)
        doc.status = Status.ARCHIVED
        db_session.commit()

        token = _login_admin(client)
        response = client.delete(
            f"/api/v1/documents/{doc.id}",
            headers=_auth_header(token),
        )

        assert response.status_code == 409


class TestHardDeleteDocument:
    def test_permanent_delete(self, client, db_session):
        mock_storage = MagicMock()
        mock_rag = MagicMock()

        doc = _create_test_document(db_session)
        doc_id = doc.id

        # Simulate an ingested document with a RAG file mapping so the
        # delete path exercises the RAG file cleanup.
        from app.modules.rag.domain.rag_file_mapping_model import RagFileMapping
        from app.shared.utils import utcnow

        now = utcnow()
        mapping = RagFileMapping(
            document_id=doc_id,
            rag_corpus_resource="projects/p/locations/l/ragCorpora/123",
            rag_file_id="456",
            rag_file_resource="projects/p/locations/l/ragCorpora/123/ragFiles/456",
            imported_at=now,
            created_at=now,
            updated_at=now,
        )
        db_session.add(mapping)
        db_session.commit()

        token = _login_admin(client)
        with _override_storage(mock_storage), _override_rag_engine(mock_rag):
            response = client.delete(
                f"/api/v1/documents/{doc_id}/permanent",
                headers=_auth_header(token),
            )

        assert response.status_code == 200
        assert response.json()["detail"] == "Document permanently deleted"
        mock_storage.delete_object.assert_called_once_with(MOCK_FILE_LINK)
        mock_rag.delete_file.assert_called_once_with(
            "projects/p/locations/l/ragCorpora/123/ragFiles/456"
        )


class TestNewVersion:
    def test_create_new_version(self, client, db_session):
        mock_adapter = MagicMock()
        mock_adapter.build_object_key.return_value = "documents/2026/05/01/abc-v2.pdf"
        mock_adapter.upload_fileobj.return_value = MOCK_FILE_LINK

        doc = _create_test_document(db_session)
        token = _login_admin(client)
        with _override_storage(mock_adapter):
            response = client.post(
                f"/api/v1/documents/{doc.id}/new-version",
                headers=_auth_header(token),
                files={
                    "file": ("v2.pdf", io.BytesIO(b"v2 content"), "application/pdf")
                },
            )

        assert response.status_code == 201
        payload = response.json()
        assert payload["version"] == 2
        assert payload["document_group_id"] == str(doc.document_group_id)
        assert payload["title"] == "Test Document"  # inherits from source

    def test_new_version_with_custom_title(self, client, db_session):
        mock_adapter = MagicMock()
        mock_adapter.build_object_key.return_value = "documents/2026/05/01/abc-v2.pdf"
        mock_adapter.upload_fileobj.return_value = MOCK_FILE_LINK

        doc = _create_test_document(db_session)
        token = _login_admin(client)
        with _override_storage(mock_adapter):
            response = client.post(
                f"/api/v1/documents/{doc.id}/new-version",
                headers=_auth_header(token),
                files={"file": ("v2.pdf", io.BytesIO(b"v2"), "application/pdf")},
                data={"title": "Version 2 Title"},
            )

        assert response.status_code == 201
        assert response.json()["title"] == "Version 2 Title"


class TestWorkflowEndpoints:
    """Ensure existing workflow endpoints still work with the updated code."""

    def test_submit_document(self, client, db_session):
        doc = _create_test_document(db_session)
        token = _login_admin(client)
        response = client.post(
            f"/api/v1/documents/{doc.id}/submit",
            headers=_auth_header(token),
        )

        assert response.status_code == 200
        assert response.json()["status"] == "pending_review"

    def test_approve_document(self, client, db_session):
        doc = _create_test_document(db_session)
        doc.status = Status.PENDING_REVIEW
        db_session.commit()

        token = _login_admin(client)
        # RAG ingestion runs synchronously on approve in local mode —
        # mock it so the test does not call the real RAG Engine.
        from unittest.mock import patch
        from app.modules.rag.application.services import IngestionResult

        with patch(
            "app.modules.rag.application.services.ingest_document",
            return_value=IngestionResult(
                document_id=doc.id, status="completed", message="mocked"
            ),
        ):
            response = client.post(
                f"/api/v1/documents/{doc.id}/approve",
                headers=_auth_header(token),
            )

        assert response.status_code == 200
        assert response.json()["status"] == "approved"

    def test_reject_document(self, client, db_session):
        doc = _create_test_document(db_session)
        doc.status = Status.PENDING_REVIEW
        db_session.commit()

        token = _login_admin(client)
        response = client.post(
            f"/api/v1/documents/{doc.id}/reject",
            headers=_auth_header(token),
            json={"reason": "Needs revision"},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "rejected"
