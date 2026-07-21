"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi } from "@/lib/api/admin";
import type { CreateUserRequest } from "@/types/user";

// ── Query key factory ───────────────────────────────────────────────────────

export const adminKeys = {
  all: ["admin"] as const,
  users: () => [...adminKeys.all, "users"] as const,
  userList: (params?: { page?: number; page_size?: number }) =>
    [...adminKeys.users(), "list", params] as const,
  userDetail: (userId: string) =>
    [...adminKeys.users(), "detail", userId] as const,
  roles: () => [...adminKeys.all, "roles"] as const,
};

// ── Queries ─────────────────────────────────────────────────────────────────

export function useAdminUsers(params?: { page?: number; page_size?: number }) {
  return useQuery({
    queryKey: adminKeys.userList(params),
    queryFn: () => adminApi.listUsers(params),
  });
}

export function useAdminUser(userId: string) {
  return useQuery({
    queryKey: adminKeys.userDetail(userId),
    queryFn: () => adminApi.getUser(userId),
    enabled: Boolean(userId),
  });
}

export function useAdminRoles() {
  return useQuery({
    queryKey: adminKeys.roles(),
    queryFn: () => adminApi.listRoles(),
  });
}

// ── Mutations ───────────────────────────────────────────────────────────────

export function useCreateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateUserRequest) => adminApi.createUser(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: adminKeys.users() });
    },
  });
}

export function useAssignRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, roleName }: { userId: string; roleName: string }) =>
      adminApi.assignRole(userId, roleName),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: adminKeys.userDetail(vars.userId) });
      qc.invalidateQueries({ queryKey: adminKeys.users() });
    },
  });
}

export function useRemoveRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, roleName }: { userId: string; roleName: string }) =>
      adminApi.removeRole(userId, roleName),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: adminKeys.userDetail(vars.userId) });
      qc.invalidateQueries({ queryKey: adminKeys.users() });
    },
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: ({ userId, newPassword }: { userId: string; newPassword: string }) =>
      adminApi.resetPassword(userId, newPassword),
  });
}
