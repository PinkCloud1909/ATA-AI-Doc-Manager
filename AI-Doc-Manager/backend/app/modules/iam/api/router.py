from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.dependencies import require_permission
from app.modules.iam.api.schemas import (
    LoginRequest,
    MeResponse,
    PrivilegeResponse,
    RegisterRequest,
    RoleResponse,
    TokenResponse,
    UserRoleResponse,
)
from app.modules.iam.application.services import issue_access_token, register_user
from app.modules.iam.infrastructure.repositories import get_user_by_id
from app.modules.iam.domain.principal import AuthenticatedUser
from app.shared.utils import utcnow

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _build_me_response(user) -> MeResponse:
    roles = []
    for user_role in user.user_roles:
        role = user_role.role
        if role is None:
            continue
        privileges = [
            PrivilegeResponse(
                id=privilege.id,
                role_id=privilege.role_id,
                api_endpoint=privilege.api_endpoint,
                is_allowed=privilege.is_allowed,
            )
            for privilege in role.privileges
        ]
        roles.append(
            UserRoleResponse(
                id=user_role.id,
                user_id=user_role.user_id,
                role_id=user_role.role_id,
                role=RoleResponse(
                    id=role.id,
                    role_name=role.role_name,
                    description=role.description,
                    privileges=privileges,
                ),
                assigned_by=user_role.assigned_by,
                assigned_at=user_role.assigned_at,
            )
        )
    return MeResponse(
        id=user.id,
        firebase_uid=user.firebase_uid,
        username=user.username,
        email=user.email,
        last_password_changed=user.last_password_changed,
        roles=roles,
    )


@router.post("/register", response_model=MeResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    session: Annotated[Session, Depends(get_db_session)],
) -> MeResponse:
    registered_user = register_user(
        session,
        username=payload.username,
        password=payload.password,
    )
    user = get_user_by_id(session, registered_user.id)
    if user is None:
        return MeResponse(
            id=registered_user.id,
            firebase_uid=None,
            username=registered_user.username,
            email=None,
            last_password_changed=None,
            roles=[],
        )
    return _build_me_response(user)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    payload: LoginRequest,
    session: Annotated[Session, Depends(get_db_session)],
) -> TokenResponse:
    token, expires_in = issue_access_token(
        session,
        username=payload.username,
        password=payload.password,
    )
    return TokenResponse(access_token=token, expires_in=expires_in)


@router.get("/me", response_model=MeResponse, status_code=status.HTTP_200_OK)
def me(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> MeResponse:
    user = get_user_by_id(session, current_user.id)
    if user is None:
        return MeResponse(
            id=current_user.id,
            firebase_uid=None,
            username=current_user.username,
            email=None,
            last_password_changed=None,
            roles=[],
        )
    return _build_me_response(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
) -> None:
    return None


@router.post("/password-changed", status_code=status.HTTP_200_OK)
def password_changed(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> dict[str, str]:
    user = get_user_by_id(session, current_user.id)
    if user is None:
        return {"status": "ok"}
    user.last_password_changed = utcnow()
    session.commit()
    return {"status": "ok"}
