from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="A unique identifier for the chat session. If not provided, a new session will be created.")
    message: str = Field(..., description="The user's message to the agent")
    mode: str | None = "text"


class SourceReference(BaseModel):
    document_id: UUID
    document_group_id: UUID
    version: int
    original_filename: str
    gcs_path: str
    download_url: str | None = None
    relevance_score: float | None = None


class ChatResponse(BaseModel):
    session_id: str = Field(..., description="The unique identifier for the chat session used")
    response: str = Field(..., description="The agent's response")
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    is_from_kb: bool = False
    model_used: str = "local-runbook-fallback"
