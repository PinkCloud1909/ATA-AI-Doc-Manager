from fastapi import APIRouter, Depends, HTTPException
import uuid

from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.dependencies import get_current_user
from app.core.exceptions import AppError
from app.modules.documents.api.router import _download_url
from app.modules.iam.domain.principal import AuthenticatedUser
from app.modules.qa.api.schemas import ChatRequest, ChatResponse, SourceReference
from app.modules.qa.application.services import ChatService

router = APIRouter(prefix="/api/v1/qa", tags=["qa"])
chat_router = APIRouter(prefix="/api/v1", tags=["qa"])

# Create a singleton for the ChatService
chat_service = ChatService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> ChatResponse:
    try:
        session_id = request.session_id or str(uuid.uuid4())
        response_text, sources, is_from_kb = chat_service.answer(session, request.message)
        source_payload = [
            SourceReference(
                document_id=source.document.id,
                document_group_id=source.document.document_group_id,
                version=source.document.version,
                original_filename=source.document.original_filename,
                gcs_path=source.document.file_link,
                download_url=_download_url(source.document),
                relevance_score=source.score,
            )
            for source in sources
        ]
        return ChatResponse(
            session_id=session_id,
            response=response_text,
            answer=response_text,
            sources=source_payload,
            is_from_kb=is_from_kb,
        )
    except AppError:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/chat", response_model=ChatResponse)
async def chat_alias(
    request: ChatRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> ChatResponse:
    return await chat(request, current_user, session)
