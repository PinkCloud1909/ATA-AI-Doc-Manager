// types/user.ts
// Aligned with OpenAPI schemas: MeResponse, UserResponse, TokenResponse,
// LoginRequest, RegisterRequest, CreateUserRequest, AssignRoleRequest, RoleResponse

/** Returned by POST /api/v1/auth/register and GET /api/v1/auth/me */
export interface MeResponse {
  id: string;
  username: string;
  roles: string[];
  permissions: string[];
}

/** Returned by admin user endpoints */
export interface UserResponse {
  id: string;
  username: string;
  roles: string[];
}

export interface UserListResponse {
  items: UserResponse[];
  total: number;
  page: number;
  page_size: number;
}

/** POST /api/v1/auth/login request body */
export interface LoginRequest {
  username: string;
  password: string;
}

/** POST /api/v1/auth/register request body */
export interface RegisterRequest {
  username: string;
  password: string;
}

/** POST /api/v1/auth/login response */
export interface TokenResponse {
  access_token: string;
  token_type?: string;
  expires_in: number;
}

/** POST /api/v1/admin/users request body */
export interface CreateUserRequest {
  username: string;
  password: string;
  roles?: string[];
}

/** POST /api/v1/admin/users/{id}/roles request body */
export interface AssignRoleRequest {
  role_name: string;
}

/** GET /api/v1/admin/roles response item */
export interface RoleResponse {
  id: string;
  role_name: string;
  description?: string | null;
}
