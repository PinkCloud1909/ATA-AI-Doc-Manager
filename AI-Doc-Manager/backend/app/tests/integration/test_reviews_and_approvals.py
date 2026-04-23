import uuid

from app.modules.documents.domain.models import Document
from app.modules.iam.domain.models import User
from app.shared.enums import DocumentType, Status
from app.shared.utils import utcnow


def _get_admin_user(db_session) -> User:
    return db_session.query(User).filter(User.username == "admin").one()


def _create_document(db_session, *, group_id, version, status, created_by):
    document = Document(
        document_group_id=group_id,
        version=version,
        document_type=DocumentType.POLICY,
        status=status,
        file_link="minio://documents/sample.pdf",
        created_by=created_by,
        created_at=utcnow(),
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    return document


def _login_admin(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    return response.json()["access_token"]


def test_submit_and_approve_expires_previous(client, db_session):
    admin = _get_admin_user(db_session)
    group_id = uuid.uuid4()

    approved_doc = _create_document(
        db_session,
        group_id=group_id,
        version=1,
        status=Status.APPROVED,
        created_by=admin.id,
    )
    draft_doc = _create_document(
        db_session,
        group_id=group_id,
        version=2,
        status=Status.DRAFT,
        created_by=admin.id,
    )

    token = _login_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    submit_response = client.post(
        f"/api/v1/documents/{draft_doc.id}/submit",
        headers=headers,
    )
    assert submit_response.status_code == 200
    assert submit_response.json()["status"] == Status.PENDING_REVIEW

    approve_response = client.post(
        f"/api/v1/documents/{draft_doc.id}/approve",
        headers=headers,
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == Status.APPROVED

    db_session.refresh(approved_doc)
    assert approved_doc.status == Status.EXPIRED


def test_reject_flow_stores_reason(client, db_session):
    admin = _get_admin_user(db_session)
    group_id = uuid.uuid4()
    draft_doc = _create_document(
        db_session,
        group_id=group_id,
        version=1,
        status=Status.DRAFT,
        created_by=admin.id,
    )

    token = _login_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    submit_response = client.post(
        f"/api/v1/documents/{draft_doc.id}/submit",
        headers=headers,
    )
    assert submit_response.status_code == 200

    reject_response = client.post(
        f"/api/v1/documents/{draft_doc.id}/reject",
        headers=headers,
        json={"reason": "Missing required sections"},
    )
    assert reject_response.status_code == 200
    payload = reject_response.json()
    assert payload["status"] == Status.REJECTED
    assert payload["rejected_reason"] == "Missing required sections"


def test_create_review_and_list(client, db_session):
    admin = _get_admin_user(db_session)
    group_id = uuid.uuid4()
    pending_doc = _create_document(
        db_session,
        group_id=group_id,
        version=1,
        status=Status.PENDING_REVIEW,
        created_by=admin.id,
    )

    token = _login_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        f"/api/v1/documents/{pending_doc.id}/reviews",
        headers=headers,
        json={"grade": 8, "comment": "Good structure and clarity."},
    )
    assert create_response.status_code == 201
    payload = create_response.json()
    assert payload["grade"] == 8
    assert payload["comment"] == "Good structure and clarity."

    list_response = client.get(
        f"/api/v1/documents/{pending_doc.id}/reviews",
        headers=headers,
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
