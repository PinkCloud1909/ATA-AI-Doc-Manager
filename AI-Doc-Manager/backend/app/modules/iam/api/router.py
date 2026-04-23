from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.dependencies import require_permission
from app.modules.iam.api.schemas import LoginRequest, MeResponse, RegisterRequest, TokenResponse
from app.modules.iam.application.services import issue_access_token, register_user
from app.modules.iam.domain.principal import AuthenticatedUser

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


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
    return MeResponse(
        id=registered_user.id,
        username=registered_user.username,
        roles=registered_user.roles,
        permissions=sorted(registered_user.permissions),
    )


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
) -> MeResponse:
    return MeResponse(
        id=current_user.id,
        username=current_user.username,
        roles=current_user.roles,
        permissions=sorted(current_user.permissions),
    )
