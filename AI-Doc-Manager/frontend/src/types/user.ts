// types/user.ts

export interface Privilege {
  id:           string
  role_id:      string
  api_endpoint: string
  is_allowed:   boolean
}

<<<<<<< Updated upstream
export interface Role {
  id:           string
  role_name:    string
  description:  string
  privileges?:  Privilege[]
=======
/** Returned by admin user endpoints */
export interface UserResponse {
  id: string;
  username: string;
  roles: string[];
  /** Effective permissions combined from every assigned role. */
  permissions: string[];
>>>>>>> Stashed changes
}

export interface UserRole {
  id:          string
  user_id:     string
  role_id:     string
  role:        Role
  assigned_by: string
  assigned_at: string
}

<<<<<<< Updated upstream
export interface User {
  id:                   string
  firebase_uid:         string   // Google UID từ Firebase
  username:             string
  email:                string
  last_password_changed: string
  roles:                UserRole[]
=======
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

/** POST /api/v1/auth/change-password request body */
export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

/** POST /api/v1/admin/users/{id}/reset-password request body */
export interface ResetPasswordRequest {
  new_password: string;
}

export interface PasswordChangeResponse {
  detail: string;
  user_id?: string;
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
  permissions: string[];
>>>>>>> Stashed changes
}
