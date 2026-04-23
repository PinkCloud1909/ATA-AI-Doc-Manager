from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.dependencies import require_permission
from app.modules.documents.api.schemas import (
    ApprovalQueueItem,
    DocumentActionResponse,
    RejectRequest,
)
from app.modules.documents.application.services import (
    approve_document,
    list_pending_approvals,
    reject_document,
    submit_document_for_review,
)
from app.modules.iam.domain.principal import AuthenticatedUser

documents_router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
approvals_router = APIRouter(prefix="/api/v1/approvals", tags=["approvals"])


def _build_document_response(document) -> DocumentActionResponse:
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
