from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Payload for a single turn of the RAG-powered Q&A chat."""

    session_id: str | None = Field(
        default=None,
        description="A unique identifier for the chat session. If not provided, a new session will be created.",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"],
    )
    message: str = Field(
        ...,
        description="The user's message or question to the RAG assistant",
        examples=["What security policies cover document access?"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "message": "What security policies cover document access?",
            }
        }
    }


class ChatResponse(BaseModel):
    """The assistant's reply for a single chat turn."""

    session_id: str = Field(
        ...,
        description="The unique identifier for the chat session (reuse in follow-up messages)",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"],
    )
    response: str = Field(
        ...,
        description="The assistant's generated answer based on retrieved document chunks",
        examples=[
            "Based on the Q4 Security Policy, document access is governed by..."
        ],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "response": "Based on the Q4 Security Policy, document access is governed by role-based permissions. Only users with the 'editor' or 'admin' role can modify documents.",
            }
        }
    }
