"""Admin API router for user & role management."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.dependencies import require_permission
from app.modules.iam.api.admin_schemas import (
    AssignRoleRequest,
    CreateUserRequest,
    PasswordResetResponse,
    ResetPasswordRequest,
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
    reset_user_password,
)
from app.modules.iam.domain.principal import AuthenticatedUser
from app.shared.openapi_helpers import DELETE_RESPONSES, LIST_RESPONSES, MUTATE_RESPONSES

admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@admin_router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user (admin)",
    description=(
        "Creates a new user with the specified roles.  "
        "Requires admin-level permissions.  The username must be unique."
    ),
    response_description="The newly created user with their assigned roles",
    responses={
        201: {"description": "User created successfully"},
        409: {"description": "Username already exists"},
        **MUTATE_RESPONSES,
    },
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
        permissions=sorted(principal.permissions),
    )


@admin_router.get(
    "/users",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all users (admin)",
    description=(
        "Returns a paginated list of all registered users.  "
        "Requires admin-level permissions."
    ),
    response_description="Paginated list of user records",
    responses=LIST_RESPONSES,
)
def list_users_route(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(default=50, ge=1, le=200, description="Items per page (1–200)"),
) -> UserListResponse:
    items, total = list_all_users(session, page=page, page_size=page_size)
    return UserListResponse(
        items=[UserResponse(**item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@admin_router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a user by ID (admin)",
    description=(
        "Returns the details of a specific user including their assigned roles.  "
        "Requires admin-level permissions."
    ),
    response_description="The requested user's details and roles",
    responses={
        404: {"description": "User not found"},
        **LIST_RESPONSES,
    },
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
    summary="Assign a role to a user (admin)",
    description=(
        "Grants an additional role to a user.  "
        "The role must already exist in the system.  "
        "Requires admin-level permissions."
    ),
    response_description="The user's updated profile with all assigned roles",
    responses={
        404: {"description": "User or role not found"},
        409: {"description": "Role is already assigned to this user"},
        **MUTATE_RESPONSES,
    },
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
    summary="Remove a role from a user (admin)",
    description=(
        "Revokes a specific role from a user.  "
        "Requires admin-level permissions."
    ),
    response_description="The user's updated profile after role removal",
    responses={
        404: {"description": "User or role not found"},
        **DELETE_RESPONSES,
    },
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


@admin_router.post(
    "/users/{user_id}/reset-password",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset a user's password (admin)",
    responses={
        404: {"description": "User not found"},
        422: {"description": "New password does not satisfy the password policy"},
        **MUTATE_RESPONSES,
    },
)
def reset_password(
    user_id: UUID,
    payload: ResetPasswordRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> PasswordResetResponse:
    reset_user_password(session, user_id=user_id, new_password=payload.new_password)
    return PasswordResetResponse(
        detail="Password reset successfully",
        user_id=user_id,
    )


@admin_router.get(
    "/roles",
    response_model=list[RoleResponse],
    status_code=status.HTTP_200_OK,
    summary="List all roles (admin)",
    description=(
        "Returns all defined security roles and their descriptions.  "
        "Requires admin-level permissions."
    ),
    response_description="List of all role definitions",
    responses={
        403: {"description": "Insufficient permissions"},
        500: {"description": "Internal server error"},
    },
)
def list_roles_route(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> list[RoleResponse]:
    roles = list_all_roles(session)
    return [RoleResponse(**r) for r in roles]
