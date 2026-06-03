"""Admin API router for user & role management."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.dependencies import require_permission
from app.modules.iam.api.admin_schemas import (
    AssignRoleRequest,
    CreateUserRequest,
    RoleResponse,
    UserListResponse,
    UserResponse,
)
from app.modules.iam.application.services import (
    assign_role_to_user,
    create_user_with_roles,
    get_user_detail,
    list_all_roles,
    list_all_users,
    remove_role_from_user,
)
from app.modules.iam.domain.principal import AuthenticatedUser

admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@admin_router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: CreateUserRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> UserResponse:
    principal = create_user_with_roles(
        session,
        username=payload.username,
        password=payload.password,
        role_names=payload.roles,
        assigned_by=current_user.id,
    )
    return UserResponse(
        id=principal.id,
        username=principal.username,
        roles=principal.roles,
    )


@admin_router.get(
    "/users",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
)
def list_users_route(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    page: int = 1,
    page_size: int = 50,
) -> UserListResponse:
    items, total = list_all_users(session, page=page, page_size=page_size)
    return UserListResponse(
        items=[UserResponse(**item) for item in items],
        total=total,
    )


@admin_router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_user(
    user_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> UserResponse:
    detail = get_user_detail(session, user_id)
    return UserResponse(**detail)


@admin_router.post(
    "/users/{user_id}/roles",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def assign_role(
    user_id: UUID,
    payload: AssignRoleRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> UserResponse:
    detail = assign_role_to_user(
        session,
        user_id=user_id,
        role_name=payload.role_name,
        assigned_by=current_user.id,
    )
    return UserResponse(**detail)


@admin_router.delete(
    "/users/{user_id}/roles/{role_name}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def remove_role(
    user_id: UUID,
    role_name: str,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> UserResponse:
    detail = remove_role_from_user(
        session,
        user_id=user_id,
        role_name=role_name,
    )
    return UserResponse(**detail)


@admin_router.get(
    "/roles",
    response_model=list[RoleResponse],
    status_code=status.HTTP_200_OK,
)
def list_roles_route(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> list[RoleResponse]:
    roles = list_all_roles(session)
    return [RoleResponse(**r) for r in roles]
