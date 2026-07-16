/**
 * lib/api/admin.ts
 *
 * Backend admin endpoints:
 *  POST   /api/v1/admin/users                        → UserResponse
 *  GET    /api/v1/admin/users                        → UserListResponse
 *  GET    /api/v1/admin/users/{id}                   → UserResponse
 *  POST   /api/v1/admin/users/{id}/roles             → UserResponse
 *  DELETE /api/v1/admin/users/{id}/roles/{role_name} → UserResponse
 *  GET    /api/v1/admin/roles                        → RoleResponse[]
 */

import apiClient from "./client";
import type {
  UserResponse,
  UserListResponse,
  CreateUserRequest,
  AssignRoleRequest,
  RoleResponse,
} from "@/types/user";

export const adminApi = {
  createUser: async (payload: CreateUserRequest): Promise<UserResponse> => {
    const { data } = await apiClient.post<UserResponse>("/admin/users", payload);
    return data;
  },

  listUsers: async (params?: {
    page?: number;
    page_size?: number;
  }): Promise<UserListResponse> => {
    const { data } = await apiClient.get<UserListResponse>("/admin/users", { params });
    return data;
  },

  getUser: async (userId: string): Promise<UserResponse> => {
    const { data } = await apiClient.get<UserResponse>(`/admin/users/${userId}`);
    return data;
  },

  assignRole: async (userId: string, roleName: string): Promise<UserResponse> => {
    const payload: AssignRoleRequest = { role_name: roleName };
    const { data } = await apiClient.post<UserResponse>(
      `/admin/users/${userId}/roles`,
      payload,
    );
    return data;
  },

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
};
