"""Pydantic schemas for admin user & role management API."""

from uuid import UUID

from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    """Payload for an admin to create a new user with initial roles."""

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
            "Initial password with uppercase, lowercase, number, special "
            "character, and no whitespace."
        ),
        examples=["SecureInitial1!"],
    )
    roles: list[str] = Field(
        default_factory=list,
        description="Role names to assign at creation time (e.g. ['editor', 'viewer'])",
        examples=[["editor", "viewer"]],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "jdoe",
                "password": "SecureInitial1!",
                "roles": ["editor", "viewer"],
            }
        }
    }


class AssignRoleRequest(BaseModel):
    """Payload to assign an additional role to a user."""

    role_name: str = Field(
        min_length=1,
        max_length=50,
        description="Name of the role to assign (e.g. 'editor', 'admin')",
        examples=["editor"],
    )

    model_config = {
        "json_schema_extra": {"example": {"role_name": "editor"}}
    }


class ResetPasswordRequest(BaseModel):
    """Payload used by an administrator to set a user's new password."""

    new_password: str = Field(
        min_length=8,
        max_length=128,
        description=(
            "New password with uppercase, lowercase, number, special character, "
            "and no whitespace."
        ),
        examples=["ResetSecure1!"],
    )


class PasswordResetResponse(BaseModel):
    detail: str
    user_id: UUID


class UserResponse(BaseModel):
    """Summary of a user account — returned by admin endpoints."""

    id: UUID = Field(
        description="Unique user identifier (UUID v4)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    username: str = Field(
        description="Registered username",
        examples=["jdoe"],
    )
    roles: list[str] = Field(
        description="Role names currently assigned to this user",
        examples=[["editor", "viewer"]],
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="Effective permission keys resolved from all assigned roles",
        examples=[["GET:/api/v1/documents", "POST:/api/v1/documents/upload"]],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "jdoe",
                "roles": ["editor", "viewer"],
            }
        }
    }


class UserListResponse(BaseModel):
    """Paginated list of users."""

    items: list[UserResponse] = Field(
        description="User records for the current page",
    )
    total: int = Field(
        description="Total number of users matching the query (across all pages)",
        examples=[42],
    )
    page: int = Field(
        description="Current page number (1-based)",
        examples=[1],
    )
    page_size: int = Field(
        description="Number of items per page",
        examples=[50],
    )


class RoleResponse(BaseModel):
    """A security role definition."""

    id: UUID = Field(
        description="Unique role identifier (UUID v4)",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    role_name: str = Field(
        description="Unique role name (e.g. 'admin', 'editor', 'viewer')",
        examples=["editor"],
    )
    description: str | None = Field(
        default=None,
        description="Human-readable description of what this role grants access to",
        examples=["Can view, edit, and submit documents for review"],
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="Allowed endpoint permissions assigned to this role",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "role_name": "editor",
                "description": "Can view, edit, and submit documents for review",
            }
        }
    }
