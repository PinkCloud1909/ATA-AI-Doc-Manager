import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token, oauth2_scheme
from app.modules.iam.application.services import load_principal
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

    token_payload = decode_access_token(token)
    try:
        user_id = UUID(token_payload.sub)
    except ValueError as exc:
        logger.warning("auth_failure", extra={"reason": "invalid_subject"})
        raise UnauthorizedError("Invalid authentication credentials") from exc

    user = load_principal(session, user_id)
    logger.info("auth_success", extra={"user_id": str(user.id), "path": request.url.path})
    return user


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
