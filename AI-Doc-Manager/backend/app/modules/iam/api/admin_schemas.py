"""Pydantic schemas for admin user & role management API."""

from uuid import UUID

from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=255)
    roles: list[str] = Field(
        default_factory=list,
        description="Role names to assign, e.g. ['editor', 'viewer']",
    )


class AssignRoleRequest(BaseModel):
    role_name: str = Field(min_length=1, max_length=50)


class UserResponse(BaseModel):
    id: UUID
    username: str
    roles: list[str]


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int


class RoleResponse(BaseModel):
    id: UUID
    role_name: str
    description: str | None = None
