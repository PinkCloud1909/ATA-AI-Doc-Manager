from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.dependencies import require_permission
from app.modules.iam.api.schemas import (
    LoginRequest,
    MeResponse,
    RegisterRequest,
    TokenResponse,
)
from app.modules.iam.application.services import issue_access_token, register_user
from app.modules.iam.domain.principal import AuthenticatedUser
from app.shared.openapi_helpers import AUTH_RESPONSES

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=MeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Creates a new user with the default 'user' role.  "
        "The username must be unique across the system.  "
        "Returns the new user's profile, roles, and resolved permissions."
    ),
    response_description="The newly created user profile with default roles and permissions",
    responses={
        409: {"description": "Username already exists"},
        **AUTH_RESPONSES,
    },
)
def register(
    payload: RegisterRequest,
    session: Annotated[Session, Depends(get_db_session)],
) -> MeResponse:
    registered_user = register_user(
        session,
        username=payload.username,
        password=payload.password,
    )
    return MeResponse(
        id=registered_user.id,
        username=registered_user.username,
        roles=registered_user.roles,
        permissions=sorted(registered_user.permissions),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Exchange credentials for a JWT access token",
    description=(
        "Authenticates the user with username and password.  "
        "Returns a signed JWT that must be included as an "
        "`Authorization: Bearer <token>` header on subsequent requests."
    ),
    response_description="JWT bearer token with expiry details",
    responses={
        401: {"description": "Invalid username or password"},
        **AUTH_RESPONSES,
    },
)
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


@router.get(
    "/me",
    response_model=MeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile and permissions",
    description=(
        "Returns the authenticated user's identity, assigned roles, "
        "and resolved permission keys.  Use this to introspect the "
        "current session and discover what actions are allowed."
    ),
    response_description="Authenticated user's identity, roles, and permission keys",
    responses={
        401: {"description": "Missing or invalid access token"},
        500: {"description": "Internal server error"},
    },
)
def me(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
) -> MeResponse:
    return MeResponse(
        id=current_user.id,
        username=current_user.username,
        roles=current_user.roles,
        permissions=sorted(current_user.permissions),
    )
