/**
 * lib/api/auth.ts
 *
 * Với kiến trúc GCP, authentication flow:
 *  1. Firebase signIn (email/password hoặc Google SSO)
 *  2. Lấy Firebase ID Token
 *  3. Backend verify token qua google-auth-library
 *  4. Backend tra cứu User trong PostgreSQL theo firebase_uid
 *
 * Frontend không gọi /auth/login nữa — Firebase handle hoàn toàn.
 * Endpoint /auth/me dùng để lấy profile + roles từ PostgreSQL.
 */

import apiClient from "./client"
import { User } from "@/types/user"
import {
  signInAndGetToken,
  signOut as firebaseSignOut,
} from "@/lib/auth/firebase"
import { mockLogin, mockMe } from "./auth.mock"

// Mock mode: không cần Firebase hay backend
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK !== "false"

export const authApi = {
  /**
   * Đăng nhập - tự động dùng mock nếu NEXT_PUBLIC_USE_MOCK=true
   */
  login: async (email: string, password: string): Promise<User> => {
    if (USE_MOCK) {
      return mockLogin(email, password)
    }
    // Bước 1: Firebase sign-in → lấy ID Token
    await signInAndGetToken(email, password)
    // Bước 2: Lấy profile + roles từ PostgreSQL
    const { data } = await apiClient.get<User>("/auth/me")
    return data
  },

  /**
   * Lấy profile hiện tại
   */
  me: async (): Promise<User> => {
    if (USE_MOCK) {
      return mockMe()
    }
    const { data } = await apiClient.get<User>("/auth/me")
    return data
  },

  /**
   * Đăng xuất: clear Firebase session + backend session.
   */
  logout: async (): Promise<void> => {
    try {
      await apiClient.post("/auth/logout")
    } finally {
      await firebaseSignOut()
    }
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
   * Đăng ký tài khoản mới
   */
  register: async (email: string, password: string): Promise<User> => {
    if (USE_MOCK) {
      return mockLogin(email, password) // Dùng lại mock login cho đơn giản
    }
    // Bước 1: Firebase create user → lấy ID Token
    await signInAndGetToken(email, password)
    // Bước 2: Tạo profile mới trên PostgreSQL (backend sẽ tự động tạo khi nhận token mới)
    const { data } = await apiClient.get<User>("/auth/me")
    return data
  },
}
