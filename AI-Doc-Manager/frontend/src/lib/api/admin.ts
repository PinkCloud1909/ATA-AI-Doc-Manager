import apiClient from "./client"
import { Role, User } from "@/types/user"

export interface CreateUserPayload {
  username: string
  password: string
  role_names: string[]
}

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
}
