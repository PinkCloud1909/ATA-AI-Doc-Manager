/**
 * lib/api/auth.ts
 *
 * Authentication flow hiện tại của backend:
 *  1. POST /api/v1/auth/login bằng username/password
 *  2. Backend trả JWT
 *  3. Axios gửi JWT trong Authorization header cho các API cần auth
 */

import apiClient from "./client"
import { User } from "@/types/user"
import { clearStoredAccessToken, setStoredAccessToken } from "./authToken"

interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

function normalizeUser(user: User): User {
  return {
    ...user,
    displayName: user.displayName ?? user.username,
    email: user.email ?? user.username,
    role:
      user.role ??
      (typeof user.roles?.[0] === "string" ? user.roles[0] : undefined),
  }
}

export const authApi = {
  /**
   * Đăng nhập qua backend FastAPI để lấy JWT.
   */
  login: async (username: string, password: string): Promise<User> => {
    const normalizedUsername = username.trim()
    const { data: token } = await apiClient.post<TokenResponse>("/auth/login", {
      username: normalizedUsername,
      password,
    })
    setStoredAccessToken(token.access_token, token.expires_in)

    const { data } = await apiClient.get<User>("/auth/me")
    return normalizeUser(data)
  },

  /**
   * Lấy profile hiện tại
   */
  me: async (): Promise<User> => {
    const { data } = await apiClient.get<User>("/auth/me")
    return normalizeUser(data)
  },

  /**
   * Đăng xuất phía client: backend hiện chưa có /auth/logout.
   */
  logout: async (): Promise<void> => {
    clearStoredAccessToken()
  },

  /**
   * Đổi mật khẩu — vẫn qua Firebase Auth
   */
  changePassword: async (newPassword: string): Promise<void> => {
    // Firebase updatePassword
    const { updatePassword } = await import("firebase/auth")
    const { firebaseAuth } = await import("@/lib/auth/firebase")
    if (!firebaseAuth.currentUser) throw new Error("Not authenticated")
    await updatePassword(firebaseAuth.currentUser, newPassword)
    // Sync timestamp về backend
    await apiClient.post("/auth/password-changed")
  },

  /**
   * Đăng ký tài khoản mới, sau đó login để lấy JWT.
   */
  register: async (username: string, password: string): Promise<User> => {
    const normalizedUsername = username.trim()
    await apiClient.post<User>("/auth/register", {
      username: normalizedUsername,
      password,
    })
    return authApi.login(normalizedUsername, password)
  },
}
