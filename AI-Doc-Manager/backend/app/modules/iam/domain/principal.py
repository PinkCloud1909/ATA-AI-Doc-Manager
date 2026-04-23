from dataclasses import dataclass, field
from uuid import UUID


@dataclass(slots=True)
class AuthenticatedUser:
    id: UUID
    username: str
    roles: list[str] = field(default_factory=list)
    permissions: set[str] = field(default_factory=set)

    def has_permission(self, permission_key: str) -> bool:
        return permission_key in self.permissions
