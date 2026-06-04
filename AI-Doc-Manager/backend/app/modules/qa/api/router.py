from fastapi import APIRouter, Depends, HTTPException
import uuid

from app.core.dependencies import get_current_user
from app.core.exceptions import AppError
from app.modules.iam.domain.principal import AuthenticatedUser
from app.modules.qa.api.schemas import ChatRequest, ChatResponse
from app.modules.qa.application.services import ChatService

router = APIRouter(prefix="/api/v1/qa", tags=["qa"])

# Create a singleton for the ChatService
chat_service = ChatService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> ChatResponse:
    try:
        session_id = request.session_id or str(uuid.uuid4())
        response_text = await chat_service.chat(
            user_id=str(current_user.id),
            session_id=session_id,
            message=request.message,
        )
        return ChatResponse(session_id=session_id, response=response_text)
    except AppError:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
