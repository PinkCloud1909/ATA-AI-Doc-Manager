from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="A unique identifier for the chat session. If not provided, a new session will be created.")
    message: str = Field(..., description="The user's message to the agent")


class ChatResponse(BaseModel):
    session_id: str = Field(..., description="The unique identifier for the chat session used")
    response: str = Field(..., description="The agent's response")
