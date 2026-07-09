/**
 * Mock auth API - không cần Firebase
 * Bật mock bằng cách set NEXT_PUBLIC_USE_MOCK=true
 */

import { User } from "@/types/user"

const mockUser: User = {
  id: "1",
  firebase_uid: "mock-admin",
  username: "Admin User",
  email: "admin@company.com",
  last_password_changed: new Date(0).toISOString(),
  roles: [
    {
      id: "mock-user-role-admin",
      user_id: "1",
      role_id: "mock-role-admin",
      assigned_by: "system",
      assigned_at: new Date(0).toISOString(),
      role: {
        id: "mock-role-admin",
        role_name: "Admin",
        description: "Mock administrator",
      },
    },
  ],
}

export async function mockLogin(email: string, password: string): Promise<User> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 500))

  // Simple validation
  if (!email || !password) {
    throw new Error("Email và mật khẩu không được để trống")
  }

  // Accept any email/password for demo
  return { ...mockUser, email, username: email.split("@")[0] || mockUser.username }
}

export async function mockMe(): Promise<User> {
  await new Promise((resolve) => setTimeout(resolve, 200))
  return mockUser
}
