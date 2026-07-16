import logging
import tempfile
from typing import Annotated, BinaryIO
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
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
    expire_document,
    get_document_detail,
    list_documents,
    list_pending_approvals,
    reject_document,
    submit_document_for_review,
    update_document_metadata,
)
from app.shared.adapters.factory import (
    get_object_storage,
    get_rag_engine,
)
from app.shared.interfaces import IObjectStorage, IRagEngine
from app.modules.iam.domain.principal import AuthenticatedUser
from app.modules.iam.domain.permissions import get_allowed_statuses
from app.shared.enums import DocumentType, Status
from app.shared.openapi_helpers import (
    DELETE_RESPONSES,
    LIST_RESPONSES,
    MUTATE_RESPONSES,
    RESPONSE_DESCRIPTIONS,
)
from app.shared.task_publisher import enqueue_rag_ingestion_task, is_async_mode

logger = logging.getLogger(__name__)

documents_router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
approvals_router = APIRouter(prefix="/api/v1/approvals", tags=["approvals"])


def _get_storage() -> IObjectStorage:
    return get_object_storage()


def _get_rag_engine_dep() -> IRagEngine:
    return get_rag_engine()


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


def _read_upload_chunked(
    file: UploadFile,
    max_bytes: int,
) -> tuple[BinaryIO, int]:
    """Read an upload once, enforcing the size limit early."""
    _CHUNK = 64 * 1024
    total = 0
    max_mb = max_bytes // (1024 * 1024)
    buffer = tempfile.SpooledTemporaryFile(max_size=max_bytes)
    while chunk := file.file.read(_CHUNK):
        total += len(chunk)
        if total > max_bytes:
            buffer.close()
            raise ValidationError(f"File size exceeds maximum of {max_mb} MB")
        buffer.write(chunk)
    buffer.seek(0)
    return buffer, total


# --- Document CRUD ---


@documents_router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new document",
    description=(
        "Upload a document file to the system.  The file is stored in object "
        "storage (Google Cloud Storage) and metadata is "
        "recorded in the database.\n\n"
        "**Supported formats**: PDF, DOCX, TXT, and common image formats.\n\n"
        "- `title` and `description` are optional — title defaults to the original filename.\n"
        "- `document_type` defaults to `other` if not specified."
    ),
    response_description="Metadata for the newly uploaded document",
    responses={
        413: {"description": RESPONSE_DESCRIPTIONS[413]},
        **MUTATE_RESPONSES,
    },
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

    file_buf, file_size = _read_upload_chunked(file, max_bytes)

    original_filename = file.filename or "upload"
    resolved_title = title or original_filename

    object_key = storage.build_object_key(original_filename)
    try:
        file_link = storage.upload_fileobj(
            file_obj=file_buf,
            object_key=object_key,
            content_type=file.content_type,
            length=file_size,
        )
    finally:
        file_buf.close()

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
    summary="List documents",
    description=(
        "Returns a paginated, filterable list of documents scoped to the "
        "authenticated user's role-based visibility.\n\n"
        "- **status_filter**: Restrict to documents in a specific lifecycle status.\n"
        "- **document_type**: Filter by document category (policy, manual, report, other).\n"
        "- **created_by**: Filter by the UUID of the document creator.\n"
        "- **page** / **page_size**: Control pagination (max 100 per page)."
    ),
    response_description="Paginated list of document summaries",
    responses=LIST_RESPONSES,
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

    allowed = get_allowed_statuses(current_user.roles)
    documents, total = list_documents(
        session,
        page=page,
        page_size=page_size,
        status_filter=status_filter,
        document_type_filter=document_type,
        created_by_filter=created_by,
        allowed_statuses=allowed if allowed else None,
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
    summary="Get document details",
    description=(
        "Returns full document metadata including its workflow history "
        "(who submitted, approved, or rejected it and when) and a "
        "time-limited presigned download URL for the file contents."
    ),
    response_description="Full document details with download URL",
    responses={
        404: {"description": RESPONSE_DESCRIPTIONS[404]},
        **MUTATE_RESPONSES,
    },
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
        rag_ingestion_status=document.rag_ingestion_status.value,
        rag_ingestion_error=document.rag_ingestion_error,
        rag_ingested_at=document.rag_ingested_at,
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
    summary="Update document metadata",
    description=(
        "Update the title, description, or document type of an existing document.  "
        "Only the fields provided are changed — omitted fields keep their current values."
    ),
    response_description="Updated document metadata",
    responses={
        404: {"description": RESPONSE_DESCRIPTIONS[404]},
        **MUTATE_RESPONSES,
    },
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
    summary="Archive a document (soft delete)",
    description=(
        "Archives a document by setting its status to `archived`.  "
        "The document and its file are retained but hidden from normal listings.  "
        "Use `/permanent` to fully delete."
    ),
    response_description="Confirmation that the document was archived",
    responses={
        404: {"description": RESPONSE_DESCRIPTIONS[404]},
        **DELETE_RESPONSES,
    },
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
    summary="Permanently delete a document",
    description=(
        "Irreversibly deletes a document, its stored file, and all associated "
        "vector embeddings.  This action cannot be undone."
    ),
    response_description="Confirmation that the document was permanently deleted",
    responses={
        404: {"description": RESPONSE_DESCRIPTIONS[404]},
        **DELETE_RESPONSES,
    },
)
def hard_delete_document(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    storage: Annotated[IObjectStorage, Depends(_get_storage)],
    rag_engine: Annotated[IRagEngine, Depends(_get_rag_engine_dep)],
) -> DocumentDeleteResponse:
    delete_document_permanently(
        session,
        document_id=document_id,
        storage=storage,
        rag_engine=rag_engine,
    )
    return DocumentDeleteResponse(
        detail="Document permanently deleted",
        document_id=document_id,
    )


@documents_router.post(
    "/{document_id}/new-version",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new version of a document",
    description=(
        "Uploads a new file as the next version of an existing document.  "
        "The version number is automatically incremented.  "
        "The new version starts in `draft` status."
    ),
    response_description="Metadata for the newly created version",
    responses={
        404: {"description": RESPONSE_DESCRIPTIONS[404]},
        413: {"description": RESPONSE_DESCRIPTIONS[413]},
        **MUTATE_RESPONSES,
    },
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

    file_buf, file_size = _read_upload_chunked(file, max_bytes)

    original_filename = file.filename or "upload"
    object_key = storage.build_object_key(original_filename)
    file_link = storage.upload_fileobj(
        file_obj=file_buf,
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
    summary="Submit a document for review",
    description=(
        "Transitions a document from `draft` to `pending_review` status.  "
        "The document then appears in the approvals queue for reviewers to act on."
    ),
    response_description="The document's updated workflow status",
    responses={
        404: {"description": RESPONSE_DESCRIPTIONS[404]},
        409: {"description": "Document is not in a state that allows submission (must be 'draft')"},
        **MUTATE_RESPONSES,
    },
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
    summary="Approve a document and trigger RAG ingestion",
    description=(
        "Approves a submitted document and triggers RAG Engine ingestion for semantic search.\n\n"
        "- **Production** (ENVIRONMENT=production + CLOUD_TASKS_QUEUE_NAME set): "
        "Enqueues a Cloud Tasks task to ingest asynchronously and returns 200 immediately.\n"
        "- **Local / dev**: Runs ingestion synchronously — RAG Engine handles "
        "parsing/chunking/embedding server-side, so the request completes in seconds.\n\n"
        "If ingestion fails, the document remains approved and a 500 is returned.  "
        "The client can manually retry via `POST /api/v1/rag/{document_id}`."
    ),
    response_description="The document's updated workflow status after approval",
    responses={
        404: {"description": RESPONSE_DESCRIPTIONS[404]},
        409: {"description": "Document is not in 'pending_review' status"},
        500: {"description": "Document approved but RAG ingestion failed"},
        **MUTATE_RESPONSES,
    },
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

    settings = get_settings()
    if is_async_mode(settings):
        try:
            enqueue_rag_ingestion_task(
                document_id=str(document_id),
                force=False,
                settings=settings,
            )
            # Mark as PENDING so the status is visible before the
            # Cloud Tasks worker picks it up.
            from app.modules.rag.application.services import (  # noqa: PLC0415
                mark_ingestion_pending,
            )
            mark_ingestion_pending(session, document_id)
            logger.info(
                "rag_ingestion_task_enqueued",
                extra={"document_id": str(document_id)},
            )
        except Exception as exc:
            logger.error(
                "rag_ingestion_enqueue_failed",
                extra={"document_id": str(document_id), "error": str(exc)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Document approved successfully, but failed to enqueue "
                    f"RAG ingestion task: {exc}. "
                    f"You can manually retry ingestion using "
                    f"POST /api/v1/rag/{document_id}?force=true"
                ),
            )
    else:
        from app.modules.rag.application.services import (  # noqa: PLC0415
            ingest_document,
        )

        try:
            result = ingest_document(
                session,
                document_id=document_id,
                rag_engine=get_rag_engine(),
                settings=settings,
            )
            logger.info(
                "rag_ingestion_sync_complete",
                extra={
                    "document_id": str(document_id),
                    "processing_time_ms": result.processing_time_ms,
                },
            )
        except Exception as exc:
            logger.error(
                "rag_ingestion_sync_failed",
                extra={"document_id": str(document_id), "error": str(exc)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Document approved successfully, but RAG ingestion failed: {exc}. "
                    f"You can manually retry ingestion using "
                    f"POST /api/v1/rag/{document_id}?force=true"
                ),
            )

    return _build_action_response(document)


@documents_router.post(
    "/{document_id}/reject",
    response_model=DocumentActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject a submitted document",
    description=(
        "Rejects a document that is pending review, with a required reason explaining "
        "what needs to change before the document can be approved."
    ),
    response_description="The document's updated workflow status after rejection",
    responses={
        404: {"description": RESPONSE_DESCRIPTIONS[404]},
        409: {"description": "Document is not in 'pending_review' status"},
        **MUTATE_RESPONSES,
    },
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


@documents_router.post(
    "/{document_id}/expire",
    response_model=DocumentActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Expire an approved document",
    description=(
        "Sets an approved document to `expired` status.  "
        "Expired documents are no longer considered current but remain searchable."
    ),
    response_description="The document's updated workflow status after expiry",
    responses={
        404: {"description": RESPONSE_DESCRIPTIONS[404]},
        409: {"description": "Document is not in 'approved' status"},
        **MUTATE_RESPONSES,
    },
)
def expire_document_route(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentActionResponse:
    document = expire_document(
        session,
        document_id=document_id,
        user_id=current_user.id,
    )
    return _build_action_response(document)


@approvals_router.get(
    "/pending",
    response_model=list[ApprovalQueueItem],
    status_code=status.HTTP_200_OK,
    summary="List pending approvals",
    description=(
        "Returns all documents currently awaiting review (`pending_review` status).  "
        "Reviewers should use this endpoint to find documents needing their attention."
    ),
    response_description="List of documents awaiting approval",
    responses={
        403: {"description": RESPONSE_DESCRIPTIONS[403]},
        500: {"description": RESPONSE_DESCRIPTIONS[500]},
    },
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
