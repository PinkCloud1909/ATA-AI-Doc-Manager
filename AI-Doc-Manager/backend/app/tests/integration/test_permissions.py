import uuid

from app.modules.documents.domain.models import Document
from app.modules.iam.domain.models import User
from app.shared.enums import DocumentType, Status
from app.shared.utils import utcnow


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _login(client, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _admin_token(client) -> str:
    return _login(client, "admin", "Admin123!")


def _create_user_with_roles(client, username: str, roles: list[str]) -> str:
    response = client.post(
        "/api/v1/admin/users",
        headers=_auth_header(_admin_token(client)),
        json={
            "username": username,
            "password": "Password123!",
            "role_names": roles,
        },
    )
    assert response.status_code == 201
    return _login(client, username, "Password123!")


def _admin_user(db_session) -> User:
    return db_session.query(User).filter(User.username == "admin").one()


def _create_document(db_session, *, status: Status, title: str) -> Document:
    admin = _admin_user(db_session)
    now = utcnow()
    document = Document(
        document_group_id=uuid.uuid4(),
        version=1,
        document_type=DocumentType.REPORT,
        status=status,
        title=title,
        description=f"{title} description",
        original_filename=f"{title}.pdf",
        file_link=f"local://documents/test/{title}.pdf",
        file_size=128,
        content_type="application/pdf",
        created_by=admin.id,
        created_at=now,
        modified_by=admin.id,
        modified_date=now,
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    return document


def test_admin_can_manage_users_and_roles(client):
    token = _admin_token(client)

    roles_response = client.get("/api/v1/admin/roles", headers=_auth_header(token))
    assert roles_response.status_code == 200
    role_names = {role["role_name"] for role in roles_response.json()}
    assert {"viewer", "editor", "reviewer", "admin"}.issubset(role_names)

    create_response = client.post(
        "/api/v1/admin/users",
        headers=_auth_header(token),
        json={
            "username": "reviewer01",
            "password": "Password123!",
            "role_names": ["reviewer"],
        },
    )
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]
    assert create_response.json()["roles"][0]["role"]["role_name"] == "reviewer"

    assign_response = client.put(
        f"/api/v1/admin/users/{user_id}/roles",
        headers=_auth_header(token),
        json={"role_names": ["editor"]},
    )
    assert assign_response.status_code == 200
    assert [role["role"]["role_name"] for role in assign_response.json()["roles"]] == [
        "editor"
    ]


def test_viewer_only_lists_approved_and_expired_documents(client, db_session):
    approved = _create_document(db_session, status=Status.APPROVED, title="approved")
    expired = _create_document(db_session, status=Status.EXPIRED, title="expired")
    draft = _create_document(db_session, status=Status.DRAFT, title="draft")
    pending = _create_document(db_session, status=Status.PENDING_REVIEW, title="pending")

    token = _create_user_with_roles(client, "viewer01", ["viewer"])
    response = client.get("/api/v1/documents", headers=_auth_header(token))

    assert response.status_code == 200
    document_ids = {item["id"] for item in response.json()["items"]}
    assert document_ids == {str(approved.id), str(expired.id)}

    draft_response = client.get(
        f"/api/v1/documents/{draft.id}",
        headers=_auth_header(token),
    )
    assert draft_response.status_code == 403

    pending_response = client.get(
        f"/api/v1/documents/{pending.id}",
        headers=_auth_header(token),
    )
    assert pending_response.status_code == 403


def test_editor_can_create_and_submit_but_cannot_approve(client, db_session):
    token = _create_user_with_roles(client, "editor01", ["editor"])
    create_response = client.post(
        "/api/v1/documents",
        headers=_auth_header(token),
        json={
            "document_type": "report",
            "file_link": "local://documents/editor-created.pdf",
            "title": "Editor document",
            "original_filename": "editor-created.pdf",
        },
    )
    assert create_response.status_code == 201
    document_id = create_response.json()["id"]

    submit_response = client.post(
        f"/api/v1/documents/{document_id}/submit",
        headers=_auth_header(token),
    )
    assert submit_response.status_code == 200
    assert submit_response.json()["status"] == Status.PENDING_REVIEW

    approve_response = client.post(
        f"/api/v1/documents/{document_id}/approve",
        headers=_auth_header(token),
    )
    assert approve_response.status_code == 403


def test_reviewer_can_approve_and_expire_but_cannot_create(client, db_session):
    token = _create_user_with_roles(client, "reviewer02", ["reviewer"])
    pending = _create_document(
        db_session,
        status=Status.PENDING_REVIEW,
        title="pending-reviewer",
    )

    create_response = client.post(
        "/api/v1/documents",
        headers=_auth_header(token),
        json={
            "document_type": "report",
            "file_link": "local://documents/reviewer-created.pdf",
            "title": "Reviewer document",
            "original_filename": "reviewer-created.pdf",
        },
    )
    assert create_response.status_code == 403

    approve_response = client.post(
        f"/api/v1/documents/{pending.id}/approve",
        headers=_auth_header(token),
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == Status.APPROVED

    expire_response = client.post(
        f"/api/v1/documents/{pending.id}/expire",
        headers=_auth_header(token),
    )
    assert expire_response.status_code == 200
    assert expire_response.json()["status"] == Status.EXPIRED
