from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import tất cả models ở đây để Alembic autogenerate detect được
from app.models.user import User, Role, Privilege, UserRole  # noqa: F401, E402
from app.models.document import Document, DocumentReview     # noqa: F401, E402
from app.models.chat import ChatSession, ChatMessage         # noqa: F401, E402
