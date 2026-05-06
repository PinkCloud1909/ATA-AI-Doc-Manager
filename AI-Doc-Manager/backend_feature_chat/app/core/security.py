"""
core/security.py
Verify Firebase ID Token và extract user identity.
FastAPI dependency: get_current_user()
"""
from __future__ import annotations

import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.db.session import AsyncSession, get_db
from app import models

# ── Khởi tạo Firebase Admin SDK (singleton) ───────────────────────────────────
_firebase_app: firebase_admin.App | None = None

def _get_firebase_app() -> firebase_admin.App:
    global _firebase_app
    if _firebase_app is None:
        # Trên Cloud Run: dùng Application Default Credentials (ADC)
        # Local dev: set GOOGLE_APPLICATION_CREDENTIALS env var
        cred = credentials.ApplicationDefault()
        _firebase_app = firebase_admin.initialize_app(cred, {
            "projectId": settings.FIREBASE_PROJECT_ID or settings.GCP_PROJECT_ID,
        })
    return _firebase_app


# ── Bearer token scheme ───────────────────────────────────────────────────────
_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> models.User:
    """
    FastAPI dependency — dùng trên mọi protected endpoint.
    1. Verify Firebase ID Token
    2. Tra cứu User trong PostgreSQL theo firebase_uid
    3. Tạo user mới nếu là lần đăng nhập đầu tiên
    """
    token = credentials.credentials

    try:
        _get_firebase_app()
        decoded = firebase_auth.verify_id_token(token)
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token hết hạn")
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token không hợp lệ")
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Xác thực thất bại")

    firebase_uid: str = decoded["uid"]
    email: str = decoded.get("email", "")

    # Tra cứu hoặc tạo mới user
    from sqlalchemy import select
    result = await db.execute(
        select(models.User).where(models.User.firebase_uid == firebase_uid)
    )
    user = result.scalar_one_or_none()

    if user is None:
        # First login — tạo user với role Viewer mặc định
        user = models.User(
            firebase_uid=firebase_uid,
            username=email.split("@")[0],
            email=email,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


# ── Permission checks ─────────────────────────────────────────────────────────
def require_roles(*role_names: str):
    """
    Dependency factory: chỉ cho phép user có role trong danh sách.
    Dùng: Depends(require_roles("Admin", "Reviewer"))
    """
    async def _check(user: models.User = Depends(get_current_user)) -> models.User:
        user_roles = {ur.role.role_name for ur in user.user_roles}
        if not user_roles.intersection(set(role_names)):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Yêu cầu role: {', '.join(role_names)}",
            )
        return user
    return _check
