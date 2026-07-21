from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=255)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=255)

<<<<<<< Updated upstream

class AdminUserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=255)
    role_names: list[str] = Field(default_factory=lambda: ["viewer"])


class AssignRolesRequest(BaseModel):
    role_names: list[str] = Field(min_length=1)
=======
    username: str = Field(
        min_length=3,
        max_length=100,
        description="Desired username (3–100 characters, unique across the system)",
        examples=["jdoe"],
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description=(
            "Account password. Must include uppercase, lowercase, number, "
            "special character, and no whitespace."
        ),
        examples=["SecurePass1!"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {"username": "jdoe", "password": "SecurePass1!"}
        }
    }
>>>>>>> Stashed changes


class ChangePasswordRequest(BaseModel):
    """Authenticated password-change payload."""

    current_password: str = Field(min_length=1, max_length=255)
    new_password: str = Field(
        min_length=8,
        max_length=128,
        description=(
            "New password with uppercase, lowercase, number, special character, "
            "and no whitespace."
        ),
        examples=["NewSecurePass1!"],
    )


class PasswordChangeResponse(BaseModel):
    detail: str


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
