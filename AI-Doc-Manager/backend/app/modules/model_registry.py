"""Imports all ORM models so SQLAlchemy metadata stays complete."""

from app.modules.documents.domain.chunk_model import DocumentChunk
from app.modules.documents.domain.models import Document
from app.modules.iam.domain.models import Privilege, Role, User, UserRole
from app.modules.reviews.domain.models import DocumentReview
from app.modules.runbooks.domain.models import Runbook

__all__ = [
    "Document",
    "DocumentChunk",
    "DocumentReview",
    "Privilege",
    "Role",
    "User",
    "UserRole",
    "Runbook",
]
