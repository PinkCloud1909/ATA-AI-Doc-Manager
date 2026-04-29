/**
 * Mock auth API - không cần Firebase
 * Bật mock bằng cách set NEXT_PUBLIC_USE_MOCK=true
 */

import { User } from "@/types/user"

const mockUser: User = {
  id: "1",
  email: "admin@company.com",
  displayName: "Admin User",
  role: "admin",
  permissions: ["read", "write", "delete", "manage_users"],
}

export async function mockLogin(email: string, password: string): Promise<User> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 500))

  // Simple validation
  if (!email || !password) {
    throw new Error("Email và mật khẩu không được để trống")
  }

  // Accept any email/password for demo
  return { ...mockUser, email }
}

export async function mockMe(): Promise<User> {
  await new Promise((resolve) => setTimeout(resolve, 200))
  return mockUser
}