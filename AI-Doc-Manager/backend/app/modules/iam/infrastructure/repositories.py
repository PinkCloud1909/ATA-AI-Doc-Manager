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
