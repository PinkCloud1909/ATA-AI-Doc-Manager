"""Imports all ORM models so SQLAlchemy metadata stays complete."""

from app.modules.documents.domain.models import Document
from app.modules.iam.domain.models import Privilege, Role, User, UserRole
from app.modules.reviews.domain.models import DocumentReview
from app.modules.runbooks.domain.models import Runbook

__all__ = [
    "Document",
    "DocumentReview",
    "Privilege",
    "Role",
    "User",
    "UserRole",
    "Runbook",
]
