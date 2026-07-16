from uuid import UUID

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Credentials for obtaining a JWT access token."""

    username: str = Field(
        min_length=1,
        max_length=100,
        description="Registered username (1–100 characters)",
        examples=["jdoe"],
    )
    password: str = Field(
        min_length=1,
        max_length=255,
        description="Account password (1–255 characters)",
        examples=["my-secure-password"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {"username": "jdoe", "password": "my-secure-password"}
        }
    }


class RegisterRequest(BaseModel):
    """New user registration payload."""

    username: str = Field(
        min_length=3,
        max_length=100,
        description="Desired username (3–100 characters, unique across the system)",
        examples=["jdoe"],
    )
    password: str = Field(
        min_length=8,
        max_length=255,
        description="Account password (minimum 8 characters)",
        examples=["my-secure-password"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {"username": "jdoe", "password": "my-secure-password"}
        }
    }


class TokenResponse(BaseModel):
    """JWT access token returned on successful login."""

    access_token: str = Field(
        description="Signed JWT to include as `Authorization: Bearer <token>` in subsequent requests",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')",
        examples=["bearer"],
    )
    expires_in: int = Field(
        description="Token lifetime in seconds from the time of issuance",
        examples=[3600],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
            }
        }
    }


class MeResponse(BaseModel):
    """Authenticated user's identity, roles, and permissions."""

    id: UUID = Field(
        description="Unique user identifier (UUID v4)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    username: str = Field(
        description="Registered username",
        examples=["jdoe"],
    )
    roles: list[str] = Field(
        description="Role names assigned to this user (e.g. 'admin', 'editor', 'viewer')",
        examples=[["editor", "viewer"]],
    )
    permissions: list[str] = Field(
        description="Resolved permission keys in `METHOD:/path` format",
        examples=[["GET:/api/v1/documents", "POST:/api/v1/documents/upload"]],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "jdoe",
                "roles": ["editor", "viewer"],
                "permissions": [
                    "GET:/api/v1/documents",
                    "POST:/api/v1/documents/upload",
                ],
            }
        }
    }
