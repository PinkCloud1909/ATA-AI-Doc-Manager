"""
api/v1/endpoints/auth.py
Minimal auth endpoints — xác thực chủ yếu qua Firebase.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.security import get_current_user
from app.db.session import get_db
from app import models

router = APIRouter(prefix="/auth", tags=["Auth"])


class UserProfileResponse(BaseModel):
    id:           str
    firebase_uid: str
    username:     str
    email:        str
    roles:        list[dict]

    model_config = {"from_attributes": True}


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    current_user: models.User = Depends(get_current_user),
):
    """
    Lấy profile + roles của user hiện tại.
    FE gọi ngay sau khi Firebase signIn để lấy roles về store.
    Khớp với authApi.me() trong lib/api/auth.ts.
    """
    return UserProfileResponse(
        id=str(current_user.id),
        firebase_uid=current_user.firebase_uid,
        username=current_user.username,
        email=current_user.email,
        roles=[
            {
                "id":        str(ur.role.id),
                "role_name": ur.role.role_name,
                "description": ur.role.description,
            }
            for ur in current_user.user_roles
        ],
    )


@router.post("/logout", status_code=204)
async def logout(current_user: models.User = Depends(get_current_user)):
    """
    Server-side logout (optional — Firebase session tự quản lý phía client).
    Có thể dùng để audit log hoặc revoke custom claims.
    """
    pass


@router.post("/password-changed", status_code=204)
async def password_changed(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cập nhật last_password_changed timestamp sau khi FE đổi mật khẩu qua Firebase."""
    from datetime import datetime, timezone
    current_user.last_password_changed = datetime.now(timezone.utc)
