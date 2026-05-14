import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db_session
from app.core.dependencies import require_permission
from app.core.exceptions import ValidationError
from app.modules.documents.api.schemas import (
    ApprovalQueueItem,
    DocumentActionResponse,
    DocumentDeleteResponse,
    DocumentDetailResponse,
    DocumentListItem,
    DocumentListResponse,
    DocumentUpdateRequest,
    DocumentUploadResponse,
    RejectRequest,
)
from app.modules.documents.application.services import (
    approve_document,
    archive_document,
    create_document,
    create_new_version,
    delete_document_permanently,
    get_document_detail,
    list_documents,
    list_pending_approvals,
    reject_document,
    submit_document_for_review,
    update_document_metadata,
)
from app.shared.adapters.factory import (
    get_llm_provider,
    get_object_storage,
    get_vector_store,
)
from app.shared.interfaces import ILLMProvider, IObjectStorage, IVectorStore
from app.modules.iam.domain.principal import AuthenticatedUser
from app.shared.enums import DocumentType, Status

logger = logging.getLogger(__name__)

documents_router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
approvals_router = APIRouter(prefix="/api/v1/approvals", tags=["approvals"])


def _get_storage() -> IObjectStorage:
    return get_object_storage()


def _get_vectors() -> IVectorStore:
    return get_vector_store()


def _get_llm() -> ILLMProvider:
    return get_llm_provider()


def _build_action_response(document) -> DocumentActionResponse:
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


def _background_vectorize(document_id: UUID) -> None:
    """Background task: run vectorization pipeline for an approved document.

    Creates its own DB session via session_scope() to avoid sharing a session
    across threads. Errors are logged but do NOT affect the HTTP response.
    """
    from app.core.db import session_scope
    from app.modules.vectorization.application.services import vectorize_document
    from app.shared.adapters.factory import (
        get_llm_provider as _llm,
        get_object_storage as _storage,
        get_vector_store as _vectors,
    )

    with session_scope() as session:
        try:
            result = vectorize_document(
                session,
                document_id=document_id,
                storage=_storage(),
                llm_provider=_llm(),
                vector_store=_vectors(),
            )
            logger.info(
                "background_vectorize_success",
                extra={
                    "document_id": str(document_id),
                    "chunk_count": result.chunk_count,
                    "processing_time_ms": result.processing_time_ms,
                },
            )
        except Exception as exc:
            logger.error(
                "background_vectorize_failed",
                extra={"document_id": str(document_id), "error": str(exc)},
            )


# --- Document CRUD ---


@documents_router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    storage: Annotated[IObjectStorage, Depends(_get_storage)],
    file: UploadFile = File(...),
    document_type: DocumentType = Form(DocumentType.OTHER),
    title: str | None = Form(default=None),
    description: str | None = Form(default=None),
) -> DocumentUploadResponse:
    settings = get_settings()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024

    # Read file content once for size check; seek back for upload.
    # For production with very large files, consider streaming chunk-by-chunk.
    file_content = file.file.read()
    file_size = len(file_content)
    if file_size > max_bytes:
        raise ValidationError(
            f"File size exceeds maximum of {settings.max_upload_size_mb}MB"
        )
    file.file.seek(0)

    original_filename = file.filename or "upload"
    resolved_title = title or original_filename

    object_key = storage.build_object_key(original_filename)
    storage.ensure_bucket()
    file_link = storage.upload_fileobj(
        file_obj=file.file,
        object_key=object_key,
        content_type=file.content_type,
        length=file_size,
    )

    document = create_document(
        session,
        title=resolved_title,
        original_filename=original_filename,
        file_link=file_link,
        document_type=document_type,
        user_id=current_user.id,
        file_size=file_size,
        content_type=file.content_type,
        description=description,
    )

    return DocumentUploadResponse(
        document_id=document.id,
        document_group_id=document.document_group_id,
        version=document.version,
        title=document.title,
        original_filename=document.original_filename,
        document_type=document.document_type,
        status=document.status,
        file_size=document.file_size,
        content_type=document.content_type,
        created_by=document.created_by,
        created_at=document.created_at,
    )


@documents_router.get(
    "",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
)
def list_documents_route(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    page: int = 1,
    page_size: int = 20,
    status_filter: Status | None = None,
    document_type: DocumentType | None = None,
    created_by: UUID | None = None,
) -> DocumentListResponse:
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 1
    if page_size > 100:
        page_size = 100

    documents, total = list_documents(
        session,
        page=page,
        page_size=page_size,
        status_filter=status_filter,
        document_type_filter=document_type,
        created_by_filter=created_by,
    )
    return DocumentListResponse(
        items=[
            DocumentListItem(
                document_id=doc.id,
                document_group_id=doc.document_group_id,
                version=doc.version,
                title=doc.title,
                original_filename=doc.original_filename,
                document_type=doc.document_type,
                status=doc.status,
                file_size=doc.file_size,
                content_type=doc.content_type,
                created_by=doc.created_by,
                created_at=doc.created_at,
            )
            for doc in documents
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@documents_router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_document(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    storage: Annotated[IObjectStorage, Depends(_get_storage)],
) -> DocumentDetailResponse:
    document, download_url = get_document_detail(session, document_id, storage)
    return DocumentDetailResponse(
        document_id=document.id,
        document_group_id=document.document_group_id,
        version=document.version,
        title=document.title,
        description=document.description,
        original_filename=document.original_filename,
        document_type=document.document_type,
        status=document.status,
        file_size=document.file_size,
        content_type=document.content_type,
        download_url=download_url,
        is_vectorized=document.is_vectorized,
        created_by=document.created_by,
        created_at=document.created_at,
        modified_by=document.modified_by,
        modified_date=document.modified_date,
        submitted_by=document.submitted_by,
        submitted_at=document.submitted_at,
        approved_by=document.approved_by,
        approved_at=document.approved_at,
        rejected_by=document.rejected_by,
        rejected_reason=document.rejected_reason,
        rejected_at=document.rejected_at,
    )


@documents_router.put(
    "/{document_id}",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_200_OK,
)
def update_document(
    document_id: UUID,
    payload: DocumentUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentUploadResponse:
    document = update_document_metadata(
        session,
        document_id=document_id,
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        document_type=payload.document_type,
    )
    return DocumentUploadResponse(
        document_id=document.id,
        document_group_id=document.document_group_id,
        version=document.version,
        title=document.title,
        original_filename=document.original_filename,
        document_type=document.document_type,
        status=document.status,
        file_size=document.file_size,
        content_type=document.content_type,
        created_by=document.created_by,
        created_at=document.created_at,
    )


@documents_router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
    status_code=status.HTTP_200_OK,
)
def soft_delete_document(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentDeleteResponse:
    archive_document(session, document_id=document_id, user_id=current_user.id)
    return DocumentDeleteResponse(
        detail="Document archived successfully",
        document_id=document_id,
    )


@documents_router.delete(
    "/{document_id}/permanent",
    response_model=DocumentDeleteResponse,
    status_code=status.HTTP_200_OK,
)
def hard_delete_document(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    storage: Annotated[IObjectStorage, Depends(_get_storage)],
) -> DocumentDeleteResponse:
    delete_document_permanently(session, document_id=document_id, minio_adapter=storage)
    return DocumentDeleteResponse(
        detail="Document permanently deleted",
        document_id=document_id,
    )


@documents_router.post(
    "/{document_id}/new-version",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def new_version_document(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    storage: Annotated[IObjectStorage, Depends(_get_storage)],
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    description: str | None = Form(default=None),
) -> DocumentUploadResponse:
    settings = get_settings()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024

    file_content = file.file.read()
    file_size = len(file_content)
    if file_size > max_bytes:
        raise ValidationError(
            f"File size exceeds maximum of {settings.max_upload_size_mb}MB"
        )
    file.file.seek(0)

    original_filename = file.filename or "upload"
    object_key = storage.build_object_key(original_filename)
    storage.ensure_bucket()
    file_link = storage.upload_fileobj(
        file_obj=file.file,
        object_key=object_key,
        content_type=file.content_type,
        length=file_size,
    )

    document = create_new_version(
        session,
        source_document_id=document_id,
        file_link=file_link,
        original_filename=original_filename,
        user_id=current_user.id,
        file_size=file_size,
        content_type=file.content_type,
        title=title,
        description=description,
    )
    return DocumentUploadResponse(
        document_id=document.id,
        document_group_id=document.document_group_id,
        version=document.version,
        title=document.title,
        original_filename=document.original_filename,
        document_type=document.document_type,
        status=document.status,
        file_size=document.file_size,
        content_type=document.content_type,
        created_by=document.created_by,
        created_at=document.created_at,
    )


# --- Workflow ---


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
    return _build_action_response(document)


@documents_router.post(
    "/{document_id}/approve",
    response_model=DocumentActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve a document and trigger background vectorization",
)
def approve_document_route(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentActionResponse:
    """Approve the document (synchronous) then schedule vectorization as a
    non-blocking background task so the HTTP response is returned immediately.
    """
    document, _expired = approve_document(
        session,
        document_id=document_id,
        user_id=current_user.id,
    )

    # Non-blocking: vectorization runs after the response is sent.
    background_tasks.add_task(_background_vectorize, document_id)
    logger.info(
        "vectorization_scheduled",
        extra={"document_id": str(document_id)},
    )

    return _build_action_response(document)


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
    return _build_action_response(document)


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
