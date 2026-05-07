import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.exceptions import ForbiddenError, UnauthorizedError
from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import get_settings
from app.core.security import decode_access_token, oauth2_scheme
from app.modules.iam.application.services import (
    build_principal,
    get_or_create_firebase_user,
    load_principal,
)
from app.modules.iam.domain.principal import AuthenticatedUser
from app.shared.utils import build_permission_key

logger = logging.getLogger(__name__)


def get_current_user(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_db_session)],
) -> AuthenticatedUser:
    if not token:
        logger.warning("auth_failure", extra={"reason": "missing_token"})
        raise UnauthorizedError("Authentication credentials were not provided")

    settings = get_settings()
    if settings.gcp_project_id:
        try:
            claims = id_token.verify_firebase_token(
                token, requests.Request(), audience=settings.gcp_project_id
            )
            firebase_uid = claims.get("user_id") or claims.get("sub")
            if not firebase_uid:
                raise UnauthorizedError("Invalid authentication credentials")

            user = get_or_create_firebase_user(
                session,
                firebase_uid=firebase_uid,
                email=claims.get("email"),
                display_name=claims.get("name"),
            )
            principal = build_principal(user)
            logger.info(
                "auth_success", extra={"user_id": str(user.id), "path": request.url.path}
            )
            return principal
        except Exception:  # noqa: BLE001
            logger.warning("auth_firebase_fallback", extra={"path": request.url.path})

    try:
        token_payload = decode_access_token(token)
        user_id = UUID(token_payload.sub)
    except Exception as exc:  # noqa: BLE001
        logger.warning("auth_failure", extra={"reason": "invalid_token"})
        raise UnauthorizedError("Invalid authentication credentials") from exc

    principal = load_principal(session, user_id)
    logger.info(
        "auth_success", extra={"user_id": str(principal.id), "path": request.url.path}
    )
    return principal


def require_permission(permission_key: str | None = None):
    def dependency(
        request: Request,
        current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    ) -> AuthenticatedUser:
        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)
        resolved_permission = permission_key or build_permission_key(
            request.method, route_path
        )
        if not current_user.has_permission(resolved_permission):
            logger.warning(
                "authorization_failure",
                extra={
                    "user_id": str(current_user.id),
                    "permission_key": resolved_permission,
                },
            )
            raise ForbiddenError("You do not have access to this resource")
        return current_user

    return dependency
