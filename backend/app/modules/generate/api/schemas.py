from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.enums import DocumentType


class GenerateRunbookRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)
    document_type: DocumentType = DocumentType.MANUAL
    output_format: str = Field(default="docx", pattern="^(docx|pdf)$")


class GenerateRunbookResponse(BaseModel):
    id: UUID
    document_id: UUID
    document_group_id: UUID
    version: int
    title: str
    file_link: str
    download_url: str | None = None
    output_format: str
