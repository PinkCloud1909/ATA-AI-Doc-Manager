import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.db import get_db_session
from app.core.dependencies import get_current_user
from app.modules.iam.domain.principal import AuthenticatedUser
from app.modules.runbooks.api.schemas import (
    RunbookGenerateRequest,
    RunbookListItem,
    RunbookListResponse,
    RunbookResponse,
)
from app.modules.runbooks.application.services import (
    delete_runbook,
    generate_runbook_task,
    get_runbook_by_id,
    list_runbooks,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/runbooks", tags=["runbooks"])


def _build_runbook_response(runbook) -> RunbookResponse:
    return RunbookResponse(
        runbook_id=runbook.id,
        title=runbook.title,
        purpose=runbook.purpose,
        document_ids=[UUID(did) for did in runbook.document_ids],
        content=runbook.content,
        status=runbook.status,
        error_message=runbook.error_message,
        created_by=runbook.created_by,
        created_at=runbook.created_at,
        modified_date=runbook.modified_date,
    )


@router.post(
    "/generate",
    response_model=RunbookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a structured markdown runbook from vectorized documents",
)
async def generate_runbook(
    request: RunbookGenerateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    session: Annotated[get_db_session, Depends(get_db_session)],
) -> RunbookResponse:
    """Generates a markdown runbook using the specified documents and purpose."""
    runbook = await generate_runbook_task(
        session,
        document_ids=request.document_ids,
        purpose=request.purpose.value,
        title=request.title,
        user_id=current_user.id,
    )
    return _build_runbook_response(runbook)


@router.get(
    "",
    response_model=RunbookListResponse,
    status_code=status.HTTP_200_OK,
    summary="List generated runbooks",
)
def list_generated_runbooks(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    session: Annotated[get_db_session, Depends(get_db_session)],
    page: int = 1,
    page_size: int = 20,
) -> RunbookListResponse:
    """Returns a paginated list of generated runbooks."""
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 1
    if page_size > 100:
        page_size = 100

    # For simplicity, users can list all runbooks or we can filter by current_user.id.
    # In a multi-tenant or private system, filter by created_by=current_user.id.
    # We filter by current_user.id to protect privacy.
    runbooks, total = list_runbooks(
        session,
        page=page,
        page_size=page_size,
        created_by=current_user.id,
    )

    return RunbookListResponse(
        items=[
            RunbookListItem(
                runbook_id=rb.id,
                title=rb.title,
                purpose=rb.purpose,
                document_ids=[UUID(did) for did in rb.document_ids],
                status=rb.status,
                created_by=rb.created_by,
                created_at=rb.created_at,
            )
            for rb in runbooks
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{runbook_id}",
    response_model=RunbookResponse,
    status_code=status.HTTP_200_OK,
    summary="Get details of a runbook",
)
def get_runbook(
    runbook_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    session: Annotated[get_db_session, Depends(get_db_session)],
) -> RunbookResponse:
    """Returns the detailed content and metadata of a runbook by UUID."""
    runbook = get_runbook_by_id(session, runbook_id)
    return _build_runbook_response(runbook)


@router.delete(
    "/{runbook_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a runbook",
)
def remove_runbook(
    runbook_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    session: Annotated[get_db_session, Depends(get_db_session)],
) -> dict[str, str]:
    """Deletes a runbook permanently from the database."""
    delete_runbook(session, runbook_id)
    return {"detail": "Runbook deleted successfully"}
