import apiClient from "./client"
import { Role, User } from "@/types/user"

<<<<<<< Updated upstream
export interface CreateUserPayload {
  username: string
  password: string
  role_names: string[]
}
=======
import apiClient from "./client";
import type {
  UserResponse,
  UserListResponse,
  CreateUserRequest,
  AssignRoleRequest,
  RoleResponse,
  PasswordChangeResponse,
} from "@/types/user";
>>>>>>> Stashed changes

export const adminApi = {
  listRoles: async (): Promise<Role[]> => {
    const { data } = await apiClient.get<Role[]>("/admin/roles")
    return data || []
  },

  listUsers: async (): Promise<User[]> => {
    const { data } = await apiClient.get<User[]>("/admin/users")
    return data || []
  },

  createUser: async (payload: CreateUserPayload): Promise<User> => {
    const { data } = await apiClient.post<User>("/admin/users", payload)
    return data
  },

  assignRoles: async (userId: string, roleNames: string[]): Promise<User> => {
    const { data } = await apiClient.put<User>(`/admin/users/${userId}/roles`, {
      role_names: roleNames,
    })
    return data
  },
<<<<<<< Updated upstream
}
=======

  removeRole: async (userId: string, roleName: string): Promise<UserResponse> => {
    const { data } = await apiClient.delete<UserResponse>(
      `/admin/users/${userId}/roles/${roleName}`,
    );
    return data;
  },

  listRoles: async (): Promise<RoleResponse[]> => {
    const { data } = await apiClient.get<RoleResponse[]>("/admin/roles");
    return data;
  },

  resetPassword: async (
    userId: string,
    newPassword: string,
  ): Promise<PasswordChangeResponse> => {
    const { data } = await apiClient.post<PasswordChangeResponse>(
      `/admin/users/${userId}/reset-password`,
      { new_password: newPassword },
    );
    return data;
  },
};
>>>>>>> Stashed changes
