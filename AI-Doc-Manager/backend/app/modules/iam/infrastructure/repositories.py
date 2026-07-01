from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modules.iam.domain.models import Privilege, Role, User, UserRole


def get_user_by_username(session: Session, username: str) -> User | None:
    stmt = (
        select(User)
        .options(
            joinedload(User.user_roles)
            .joinedload(UserRole.role)
            .joinedload(Role.privileges)
        )
        .where(User.username == username)
    )
    return session.execute(stmt).unique().scalar_one_or_none()


def get_user_by_id(session: Session, user_id: UUID) -> User | None:
    stmt = (
        select(User)
        .options(
            joinedload(User.user_roles)
            .joinedload(UserRole.role)
            .joinedload(Role.privileges)
        )
        .where(User.id == user_id)
    )
    return session.execute(stmt).unique().scalar_one_or_none()


def get_role_by_name(session: Session, role_name: str) -> Role | None:
    stmt = select(Role).where(Role.role_name == role_name)
    return session.execute(stmt).scalar_one_or_none()


def get_privilege_by_role_and_endpoint(
    session: Session,
    role_id: UUID,
    api_endpoint: str,
) -> Privilege | None:
    stmt = select(Privilege).where(
        Privilege.role_id == role_id,
        Privilege.api_endpoint == api_endpoint,
    )
    return session.execute(stmt).scalar_one_or_none()


def list_users(
    session: Session,
    *,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[User], int]:
    """Return a paginated list of users with their roles eagerly loaded."""
    from sqlalchemy import func

    total = session.execute(select(func.count()).select_from(User)).scalar() or 0
    offset = (page - 1) * page_size
    stmt = (
        select(User)
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
        .order_by(User.username)
        .offset(offset)
        .limit(page_size)
    )
    users = session.execute(stmt).unique().scalars().all()
    return users, total


def get_user_role(
    session: Session,
    user_id: UUID,
    role_id: UUID,
) -> UserRole | None:
    """Check if a user-role assignment already exists."""
    stmt = select(UserRole).where(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id,
    )
    return session.execute(stmt).scalar_one_or_none()


def list_roles(session: Session) -> list[Role]:
    """Return all roles ordered by name."""
    stmt = select(Role).order_by(Role.role_name)
    return session.execute(stmt).scalars().all()
