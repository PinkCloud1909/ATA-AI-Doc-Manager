from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=255)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=255)


class AdminUserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=255)
    role_names: list[str] = Field(default_factory=lambda: ["viewer"])


class AssignRolesRequest(BaseModel):
    role_names: list[str] = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class PrivilegeResponse(BaseModel):
    id: UUID
    role_id: UUID | None = None
    api_endpoint: str
    is_allowed: bool | None = None


class RoleResponse(BaseModel):
    id: UUID
    role_name: str
    description: str | None = None
    privileges: list[PrivilegeResponse] = Field(default_factory=list)


class UserRoleResponse(BaseModel):
    id: UUID
    user_id: UUID
    role_id: UUID
    role: RoleResponse
    assigned_by: UUID | None = None
    assigned_at: datetime | None = None


class MeResponse(BaseModel):
    id: UUID
    firebase_uid: str | None = None
    username: str
    email: str | None = None
    last_password_changed: datetime | None = None
    roles: list[UserRoleResponse]
