import uuid
from unittest.mock import AsyncMock, patch


from app.modules.documents.domain.models import Document
from app.modules.runbooks.domain.models import Runbook
from app.shared.enums import DocumentType, Status
from app.shared.utils import utcnow


def _login_admin(client) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_vectorized_document(db_session, user_id=None) -> Document:
    now = utcnow()
    doc = Document(
        document_group_id=uuid.uuid4(),
        version=1,
        document_type=DocumentType.REPORT,
        status=Status.APPROVED,
        title="Vectorized Test Document",
        description="A test document that is vectorized",
        original_filename="test.pdf",
        file_link="minio://documents/test.pdf",
        file_size=1024,
        content_type="application/pdf",
        is_vectorized=True,
        created_by=user_id,
        created_at=now,
        modified_by=user_id,
        modified_date=now,
    )
    db_session.add(doc)
    db_session.commit()
    return doc


def _create_unvectorized_document(db_session, user_id=None) -> Document:
    now = utcnow()
    doc = Document(
        document_group_id=uuid.uuid4(),
        version=1,
        document_type=DocumentType.REPORT,
        status=Status.DRAFT,
        title="Unvectorized Test Document",
        description="A test document that is not vectorized",
        original_filename="test.pdf",
        file_link="minio://documents/test.pdf",
        file_size=1024,
        content_type="application/pdf",
        is_vectorized=False,
        created_by=user_id,
        created_at=now,
        modified_by=user_id,
        modified_date=now,
    )
    db_session.add(doc)
    db_session.commit()
    return doc


class TestGenerateRunbook:
    def test_generate_runbook_success(self, client, db_session):
        doc = _create_vectorized_document(db_session)
        token = _login_admin(client)

        mock_content = "# Generated Runbook\n\nThis is a mock onboarding runbook."

        with patch(
            "app.modules.runbooks.application.services.runbook_service.generate",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_content

            response = client.post(
                "/api/v1/runbooks/generate",
                headers=_auth_header(token),
                json={
                    "document_ids": [str(doc.id)],
                    "purpose": "onboarding",
                    "title": "Onboarding Runbook",
                },
            )

        assert response.status_code == 201
        payload = response.json()
        assert payload["title"] == "Onboarding Runbook"
        assert payload["purpose"] == "onboarding"
        assert payload["status"] == "completed"
        assert payload["content"] == mock_content
        assert payload["document_ids"] == [str(doc.id)]

    def test_generate_runbook_unvectorized_fails(self, client, db_session):
        doc = _create_unvectorized_document(db_session)
        token = _login_admin(client)

        response = client.post(
            "/api/v1/runbooks/generate",
            headers=_auth_header(token),
            json={
                "document_ids": [str(doc.id)],
                "purpose": "onboarding",
            },
        )

        assert response.status_code == 422
        assert "not vectorized yet" in response.json()["detail"]

    def test_generate_runbook_missing_document_fails(self, client, db_session):
        token = _login_admin(client)
        fake_id = str(uuid.uuid4())

        response = client.post(
            "/api/v1/runbooks/generate",
            headers=_auth_header(token),
            json={
                "document_ids": [fake_id],
                "purpose": "onboarding",
            },
        )

        assert response.status_code == 404
        assert "Documents not found" in response.json()["detail"]


class TestRunbookCrud:
    def test_get_runbook_detail(self, client, db_session):
        token = _login_admin(client)
        # Create a runbook directly in db
        now = utcnow()
        runbook = Runbook(
            title="My Runbook",
            purpose="deployment",
            document_ids=[str(uuid.uuid4())],
            status="completed",
            content="# Steps\n1. Deploy",
            created_at=now,
            modified_date=now,
        )
        db_session.add(runbook)
        db_session.commit()

        response = client.get(
            f"/api/v1/runbooks/{runbook.id}",
            headers=_auth_header(token),
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["runbook_id"] == str(runbook.id)
        assert payload["title"] == "My Runbook"
        assert payload["content"] == "# Steps\n1. Deploy"

    def test_list_runbooks(self, client, db_session):
        token = _login_admin(client)
        me_resp = client.get("/api/v1/auth/me", headers=_auth_header(token))
        user_id = uuid.UUID(me_resp.json()["id"])

        now = utcnow()
        for i in range(3):
            runbook = Runbook(
                title=f"Runbook {i}",
                purpose="troubleshooting",
                document_ids=[str(uuid.uuid4())],
                status="completed",
                created_by=user_id,
                created_at=now,
                modified_date=now,
            )
            db_session.add(runbook)
        db_session.commit()

        response = client.get(
            "/api/v1/runbooks",
            headers=_auth_header(token),
            params={"page": 1, "page_size": 2},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 3
        assert len(payload["items"]) == 2
        assert payload["page"] == 1
        assert payload["page_size"] == 2

    def test_delete_runbook(self, client, db_session):
        token = _login_admin(client)
        now = utcnow()
        runbook = Runbook(
            title="Delete Me",
            purpose="other",
            document_ids=[],
            status="completed",
            created_at=now,
            modified_date=now,
        )
        db_session.add(runbook)
        db_session.commit()
        runbook_id = runbook.id

        response = client.delete(
            f"/api/v1/runbooks/{runbook_id}",
            headers=_auth_header(token),
        )

        assert response.status_code == 200
        assert response.json()["detail"] == "Runbook deleted successfully"

        # Verify not in DB
        db_session.expire_all()
        rb_in_db = db_session.get(Runbook, runbook_id)
        assert rb_in_db is None
