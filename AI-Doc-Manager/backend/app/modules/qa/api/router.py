import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user
from app.modules.iam.domain.principal import AuthenticatedUser
from app.modules.qa.api.schemas import ChatRequest, ChatResponse
from app.modules.qa.application.services import ChatService

logger = logging.getLogger(__name__)

# Consistent with all other API routes: /api/v1/...
router = APIRouter(prefix="/api/v1/qa", tags=["qa"])

# Singleton — ChatService initializes the ADK Runner and DatabaseSessionService once.
# Both Runner and DatabaseSessionService are safe to share across requests.
chat_service = ChatService()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a message to the RAG-powered DMS assistant",
)
async def chat(
    request: ChatRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> ChatResponse:
    """Run one conversation turn.

    - If ``session_id`` is omitted a new session UUID is generated.
    - The agent automatically searches the vector store before answering.
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        response_text = await chat_service.chat(
            user_id=str(current_user.id),
            session_id=session_id,
            message=request.message,
        )
        return ChatResponse(session_id=session_id, response=response_text)
    except Exception as exc:
        logger.error(
            "chat_endpoint_error",
            extra={"error": str(exc), "user_id": str(current_user.id)},
        )
        raise HTTPException(status_code=500, detail=str(exc))
