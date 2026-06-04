from __future__ import annotations

import io
import uuid
from datetime import timedelta
from pathlib import Path
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db_session
from app.core.dependencies import require_permission
from app.core.exceptions import ForbiddenError
from app.modules.documents.api.schemas import (
    ApprovalQueueItem,
    ConfirmUploadRequest,
    DocumentActionResponse,
    DocumentCreateRequest,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentUpdateRequest,
    PaginatedDocumentsResponse,
    RejectRequest,
    SignedUploadUrlRequest,
    SignedUploadUrlResponse,
    VersionHistoryItem,
)
from app.modules.documents.application.services import (
    approve_document,
    archive_document,
    average_grade,
    create_document,
    create_new_version,
    get_document_by_id,
    get_document_versions,
    list_documents,
    list_pending_approvals,
    mark_document_expired,
    permanently_delete_document,
    reject_document,
    submit_document_for_review,
    update_document_metadata,
)
from app.modules.documents.domain.models import Document
from app.modules.iam.domain.principal import AuthenticatedUser
from app.shared.enums import DocumentType, Status
from app.shared.utils import safe_filename, utcnow

documents_router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
approvals_router = APIRouter(prefix="/api/v1/approvals", tags=["approvals"])

ROLE_VISIBLE_STATUSES: dict[str, set[Status]] = {
    "user": {Status.APPROVED, Status.EXPIRED},
    "viewer": {Status.APPROVED, Status.EXPIRED},
    "editor": {
        Status.DRAFT,
        Status.PENDING_REVIEW,
        Status.APPROVED,
        Status.REJECTED,
        Status.EXPIRED,
    },
    "reviewer": {
        Status.PENDING_REVIEW,
        Status.APPROVED,
        Status.REJECTED,
        Status.EXPIRED,
    },
}
ADMIN_ROLES = {"admin"}


class LocalStorageAdapter:
    """Local object-storage fallback for development and tests."""

    def __init__(self) -> None:
        self.root = Path(__file__).resolve().parents[5] / "storage"
        self.root.mkdir(parents=True, exist_ok=True)

    def build_object_key(self, filename: str, prefix: str = "documents") -> str:
        dated = utcnow().strftime("%Y/%m/%d")
        return f"{prefix.strip('/')}/{dated}/{uuid.uuid4().hex}-{safe_filename(filename)}"

    def upload_fileobj(
        self,
        file_obj: Any,
        object_key: str,
        content_type: str | None = None,
        length: int = -1,
    ) -> str:
        target = self.root / object_key
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as out:
            while True:
                chunk = file_obj.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
        return f"local://documents/{object_key}"

    def generate_presigned_download_url(
        self,
        object_reference: str,
        expires: timedelta | None = None,
    ) -> str:
        return object_reference

    def delete_object(self, object_reference: str) -> None:
        if not object_reference.startswith("local://documents/"):
            return
        object_key = object_reference.removeprefix("local://documents/")
        target = self.root / object_key
        if target.exists():
            target.unlink()


def _get_storage() -> LocalStorageAdapter:
    # Tests patch this symbol. In local mode, this fallback avoids requiring
    # MinIO/GCS credentials while keeping the same object-storage contract.
    return LocalStorageAdapter()


def _allowed_statuses(current_user: AuthenticatedUser) -> set[Status] | None:
    role_names = {role_name.lower() for role_name in current_user.roles}
    if role_names & ADMIN_ROLES:
        return None

    statuses: set[Status] = set()
    for role_name in role_names:
        statuses.update(ROLE_VISIBLE_STATUSES.get(role_name, set()))
    return statuses


def _ensure_can_view_document(
    current_user: AuthenticatedUser,
    document: Document,
) -> None:
    allowed_statuses = _allowed_statuses(current_user)
    if allowed_statuses is not None and document.status not in allowed_statuses:
        raise ForbiddenError("You do not have access to this document")


def _download_url(document: Document) -> str:
    if document.file_link.startswith("local://documents/"):
        return f"/api/v1/documents/{document.id}/download"
    try:
        value = _get_storage().generate_presigned_download_url(document.file_link)
        return value if isinstance(value, str) else document.file_link
    except Exception:
        return document.file_link


def _local_file_path(document: Document) -> Path | None:
    if not document.file_link.startswith("local://documents/"):
        return None
    object_key = document.file_link.removeprefix("local://documents/")
    root = Path(__file__).resolve().parents[5] / "storage"
    target = (root / object_key).resolve()
    if not str(target).startswith(str(root.resolve())):
        return None
    return target


def _review_payloads(document: Document) -> list[dict[str, Any]]:
    return [
        {
            "id": review.id,
            "document_id": review.document_id,
            "user_id": review.user_id,
            "grade": review.grade,
            "comment": review.comment,
            "created_date": review.created_date,
        }
        for review in (document.reviews or [])
    ]


def _build_list_response(
    document: Document,
    session: Session,
) -> DocumentListResponse:
    creator = document.creator
    return DocumentListResponse(
        id=document.id,
        document_id=document.id,
        document_group_id=document.document_group_id,
        version=document.version,
        document_type=document.document_type,
        status=document.status,
        title=document.title,
        description=document.description,
        file_link=document.file_link,
        original_filename=document.original_filename,
        file_size=document.file_size,
        size_bytes=document.file_size,
        content_type=document.content_type,
        is_vectorized=document.is_vectorized,
        vertex_index_id=document.vertex_index_id,
        created_by=document.created_by,
        created_by_name=creator.username if creator else None,
        created_at=document.created_at,
        avg_grade=average_grade(session, document.id),
    )


def _build_detail_response(
    document: Document,
    session: Session,
    *,
    include_download_url: bool = True,
) -> DocumentDetailResponse:
    creator = document.creator
    return DocumentDetailResponse(
        id=document.id,
        document_id=document.id,
        document_group_id=document.document_group_id,
        version=document.version,
        document_type=document.document_type,
        status=document.status,
        title=document.title,
        description=document.description,
        file_link=document.file_link,
        original_filename=document.original_filename,
        file_size=document.file_size,
        size_bytes=document.file_size,
        content_type=document.content_type,
        is_vectorized=document.is_vectorized,
        vertex_index_id=document.vertex_index_id,
        download_url=_download_url(document) if include_download_url else None,
        created_by=document.created_by,
        created_by_name=creator.username if creator else None,
        created_at=document.created_at,
        modified_by=document.modified_by,
        modified_date=document.modified_date,
        reviews=_review_payloads(document),
        avg_grade=average_grade(session, document.id),
    )


def _build_document_response(document: Document) -> DocumentActionResponse:
    return DocumentActionResponse(
        document_id=document.id,
        document_group_id=document.document_group_id,
        version=document.version,
        document_type=document.document_type,
        status=document.status,
        submitted_by=document.submitted_by,
        submitted_at=document.submitted_at,
        approved_by=document.approved_by,
        approved_at=document.approved_at,
        rejected_by=document.rejected_by,
        rejected_reason=document.rejected_reason,
        rejected_at=document.rejected_at,
    )


@documents_router.post(
    "/upload",
    response_model=DocumentDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    file: UploadFile = File(...),
    document_type: DocumentType = Form(DocumentType.OTHER),
    title: str | None = Form(None),
    description: str | None = Form(None),
) -> DocumentDetailResponse:
    content = await file.read()
    storage = _get_storage()
    object_key = storage.build_object_key(file.filename or "document")
    file_link = storage.upload_fileobj(
        io.BytesIO(content),
        object_key,
        file.content_type,
        length=len(content),
    )
    document = create_document(
        session,
        document_type=document_type,
        file_link=file_link,
        user_id=current_user.id,
        title=title or file.filename,
        description=description,
        original_filename=file.filename,
        file_size=len(content),
        content_type=file.content_type,
    )
    return _build_detail_response(document, session)


@documents_router.post(
    "/signed-upload-url",
    response_model=SignedUploadUrlResponse,
    status_code=status.HTTP_200_OK,
)
def signed_upload_url(
    payload: SignedUploadUrlRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
) -> SignedUploadUrlResponse:
    storage = _get_storage()
    object_key = storage.build_object_key(payload.filename)
    return SignedUploadUrlResponse(
        signed_url=f"local-upload://{object_key}",
        gcs_path=f"local://documents/{object_key}",
    )


@documents_router.post(
    "/confirm-upload",
    response_model=DocumentDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def confirm_upload(
    payload: ConfirmUploadRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentDetailResponse:
    if payload.document_group_id:
        existing = session.execute(
            select(Document)
            .where(Document.document_group_id == payload.document_group_id)
            .order_by(Document.version.desc())
        ).scalars().first()
        document = (
            create_new_version(
                session,
                existing.id,
                payload.gcs_path,
                current_user.id,
                title=payload.title,
                description=payload.description,
                original_filename=payload.original_filename,
                file_size=payload.size_bytes,
                content_type=payload.content_type,
            )
            if existing
            else create_document(
                session,
                payload.document_type,
                payload.gcs_path,
                current_user.id,
                title=payload.title or payload.original_filename,
                description=payload.description,
                original_filename=payload.original_filename,
                file_size=payload.size_bytes,
                content_type=payload.content_type,
                document_group_id=payload.document_group_id,
            )
        )
    else:
        document = create_document(
            session,
            payload.document_type,
            payload.gcs_path,
            current_user.id,
            title=payload.title or payload.original_filename,
            description=payload.description,
            original_filename=payload.original_filename,
            file_size=payload.size_bytes,
            content_type=payload.content_type,
        )
    return _build_detail_response(document, session)


@documents_router.post(
    "",
    response_model=DocumentDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_document(
    payload: DocumentCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentDetailResponse:
    document = create_document(
        session,
        document_type=payload.document_type,
        file_link=payload.file_link,
        user_id=current_user.id,
        title=payload.title or payload.original_filename,
        description=payload.description,
        original_filename=payload.original_filename,
        file_size=payload.file_size,
        content_type=payload.content_type,
    )
    return _build_detail_response(document, session)


@documents_router.get(
    "",
    response_model=PaginatedDocumentsResponse,
    status_code=status.HTTP_200_OK,
)
def get_all_documents(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    status_filter: Status | None = Query(None),
    status_param: Status | None = Query(None, alias="status"),
    document_type: DocumentType | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedDocumentsResponse:
    documents, total = list_documents(
        session,
        status_filter=status_filter or status_param,
        allowed_statuses=_allowed_statuses(current_user),
        document_type=document_type,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PaginatedDocumentsResponse(
        items=[_build_list_response(doc, session) for doc in documents],
        total=total,
        page=page,
        page_size=page_size,
    )


@documents_router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_document_detail(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentDetailResponse:
    document = get_document_by_id(session, document_id)
    _ensure_can_view_document(current_user, document)
    return _build_detail_response(document, session)


@documents_router.get(
    "/{document_id}/download-url",
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
)
def get_download_url(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> dict[str, str]:
    document = get_document_by_id(session, document_id)
    _ensure_can_view_document(current_user, document)
    return {"download_url": _download_url(document)}


@documents_router.get(
    "/{document_id}/download",
    status_code=status.HTTP_200_OK,
)
def download_document(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> FileResponse:
    document = get_document_by_id(session, document_id)
    _ensure_can_view_document(current_user, document)
    target = _local_file_path(document)
    if target is None or not target.exists():
        raise HTTPException(status_code=404, detail="File not found in local storage")
    return FileResponse(
        path=target,
        filename=document.original_filename,
        media_type=document.content_type or "application/octet-stream",
    )


@documents_router.get(
    "/{document_id}/versions",
    response_model=list[VersionHistoryItem],
    status_code=status.HTTP_200_OK,
)
def get_versions(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> list[VersionHistoryItem]:
    document = get_document_by_id(session, document_id)
    _ensure_can_view_document(current_user, document)
    versions = get_document_versions(session, document.document_group_id)
    allowed_statuses = _allowed_statuses(current_user)
    if allowed_statuses is not None:
        versions = [version for version in versions if version.status in allowed_statuses]
    return [
        VersionHistoryItem(
            id=v.id,
            version=v.version,
            status=v.status,
            created_at=v.created_at,
            created_by=v.created_by,
        )
        for v in versions
    ]


@documents_router.post(
    "/{document_id}/new-version",
    response_model=DocumentDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_new_version(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    file: UploadFile = File(...),
    title: str | None = Form(None),
    description: str | None = Form(None),
) -> DocumentDetailResponse:
    content = await file.read()
    storage = _get_storage()
    object_key = storage.build_object_key(file.filename or "document")
    file_link = storage.upload_fileobj(
        io.BytesIO(content),
        object_key,
        file.content_type,
        length=len(content),
    )
    document = create_new_version(
        session,
        document_id=document_id,
        file_link=file_link,
        user_id=current_user.id,
        title=title,
        description=description,
        original_filename=file.filename,
        file_size=len(content),
        content_type=file.content_type,
    )
    return _build_detail_response(document, session)


@documents_router.put(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    status_code=status.HTTP_200_OK,
)
def update_document(
    document_id: UUID,
    payload: DocumentUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentDetailResponse:
    document = update_document_metadata(
        session,
        document_id,
        current_user.id,
        title=payload.title,
        description=payload.description,
        document_type=payload.document_type,
    )
    return _build_detail_response(document, session)


@documents_router.delete(
    "/{document_id}",
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
)
def archive_document_route(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> dict[str, str]:
    archive_document(session, document_id, current_user.id)
    return {"detail": "Document archived successfully"}


@documents_router.delete(
    "/{document_id}/permanent",
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
)
def permanently_delete_document_route(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> dict[str, str]:
    document = get_document_by_id(session, document_id)
    try:
        _get_storage().delete_object(document.file_link)
    except Exception:
        pass
    permanently_delete_document(session, document_id)
    return {"detail": "Document permanently deleted"}


@documents_router.post(
    "/{document_id}/submit",
    response_model=DocumentActionResponse,
    status_code=status.HTTP_200_OK,
)
def submit_document(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentActionResponse:
    document = submit_document_for_review(
        session,
        document_id=document_id,
        user_id=current_user.id,
    )
    return _build_document_response(document)


@documents_router.post(
    "/{document_id}/approve",
    response_model=DocumentActionResponse,
    status_code=status.HTTP_200_OK,
)
def approve_document_route(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentActionResponse:
    document, _expired = approve_document(
        session,
        document_id=document_id,
        user_id=current_user.id,
    )
    return _build_document_response(document)


@documents_router.post(
    "/{document_id}/reject",
    response_model=DocumentActionResponse,
    status_code=status.HTTP_200_OK,
)
def reject_document_route(
    document_id: UUID,
    payload: RejectRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentActionResponse:
    document = reject_document(
        session,
        document_id=document_id,
        user_id=current_user.id,
        reason=payload.reason,
    )
    return _build_document_response(document)


@documents_router.post(
    "/{document_id}/expire",
    response_model=DocumentActionResponse,
    status_code=status.HTTP_200_OK,
)
def expire_document_route(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentActionResponse:
    document = mark_document_expired(
        session,
        document_id=document_id,
        user_id=current_user.id,
    )
    return _build_document_response(document)


@approvals_router.get(
    "/pending",
    response_model=list[ApprovalQueueItem],
    status_code=status.HTTP_200_OK,
)
def pending_approvals(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> list[ApprovalQueueItem]:
    documents = list_pending_approvals(session)
    return [
        ApprovalQueueItem(
            document_id=document.id,
            document_group_id=document.document_group_id,
            version=document.version,
            document_type=document.document_type,
            status=document.status,
            created_by=document.created_by,
            created_at=document.created_at,
            submitted_by=document.submitted_by,
            submitted_at=document.submitted_at,
        )
        for document in documents
    ]


@approvals_router.post(
    "/{document_id}/approve",
    response_model=DocumentActionResponse,
    status_code=status.HTTP_200_OK,
)
def approve_document_from_queue(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentActionResponse:
    document, _expired = approve_document(
        session,
        document_id=document_id,
        user_id=current_user.id,
    )
    return _build_document_response(document)


@approvals_router.post(
    "/{document_id}/reject",
    response_model=DocumentActionResponse,
    status_code=status.HTTP_200_OK,
)
def reject_document_from_queue(
    document_id: UUID,
    payload: RejectRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentActionResponse:
    document = reject_document(
        session,
        document_id=document_id,
        user_id=current_user.id,
        reason=payload.reason,
    )
    return _build_document_response(document)


@approvals_router.get(
    "/approved",
    response_model=list[ApprovalQueueItem],
    status_code=status.HTTP_200_OK,
)
def approved_documents(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> list[ApprovalQueueItem]:
    docs = session.execute(
        select(Document).where(Document.status == Status.APPROVED)
    ).scalars().all()
    return [
        ApprovalQueueItem(
            document_id=doc.id,
            document_group_id=doc.document_group_id,
            version=doc.version,
            document_type=doc.document_type,
            status=doc.status,
            created_by=doc.created_by,
            created_at=doc.created_at,
            submitted_by=doc.submitted_by,
            submitted_at=doc.submitted_at,
        )
        for doc in docs
    ]


@approvals_router.get(
    "/rejected",
    response_model=list[ApprovalQueueItem],
    status_code=status.HTTP_200_OK,
)
def rejected_documents(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> list[ApprovalQueueItem]:
    docs = session.execute(
        select(Document).where(Document.status == Status.REJECTED)
    ).scalars().all()
    return [
        ApprovalQueueItem(
            document_id=doc.id,
            document_group_id=doc.document_group_id,
            version=doc.version,
            document_type=doc.document_type,
            status=doc.status,
            created_by=doc.created_by,
            created_at=doc.created_at,
            submitted_by=doc.submitted_by,
            submitted_at=doc.submitted_at,
        )
        for doc in docs
    ]
