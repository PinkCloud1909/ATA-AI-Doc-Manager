import io

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.dependencies import require_permission
from app.modules.documents.api.router import _download_url, _get_storage
from app.modules.documents.application.services import create_document
from app.modules.generate.api.schemas import GenerateRunbookRequest, GenerateRunbookResponse
from app.modules.generate.application.services import (
    build_docx_bytes,
    build_pdf_bytes,
    build_runbook_text,
)
from app.modules.iam.domain.principal import AuthenticatedUser
from app.shared.utils import safe_filename

router = APIRouter(prefix="/api/v1/generate", tags=["generate"])


@router.post(
    "/runbook",
    response_model=GenerateRunbookResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_runbook(
    payload: GenerateRunbookRequest,
    current_user: AuthenticatedUser = Depends(require_permission()),
    session: Session = Depends(get_db_session),
) -> GenerateRunbookResponse:
    title = f"Runbook - {payload.prompt.strip()[:80]}"
    content = build_runbook_text(payload.prompt)
    if payload.output_format == "pdf":
        file_bytes = build_pdf_bytes(title, content)
        content_type = "application/pdf"
        extension = "pdf"
    else:
        file_bytes = build_docx_bytes(title, content)
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        extension = "docx"

    filename = f"{safe_filename(title)}.{extension}"
    storage = _get_storage()
    object_key = storage.build_object_key(filename, prefix="generated")
    file_link = storage.upload_fileobj(
        io.BytesIO(file_bytes),
        object_key,
        content_type,
        length=len(file_bytes),
    )
    document = create_document(
        session,
        payload.document_type,
        file_link,
        current_user.id,
        title=title,
        description=payload.prompt,
        original_filename=filename,
        file_size=len(file_bytes),
        content_type=content_type,
    )
    return GenerateRunbookResponse(
        id=document.id,
        document_id=document.id,
        document_group_id=document.document_group_id,
        version=document.version,
        title=document.title,
        file_link=document.file_link,
        download_url=_download_url(document),
        output_format=extension,
    )
