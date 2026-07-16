// types/admin.ts
// Re-exports admin-related types from user.ts and standalone admin schemas
// All types match OpenAPI spec exactly.

export type {
  UserResponse,
  UserListResponse,
  CreateUserRequest,
  AssignRoleRequest,
  RoleResponse,
} from "./user";
