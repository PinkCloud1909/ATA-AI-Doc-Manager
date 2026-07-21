import apiClient from "./client"
import { clearStoredAccessToken, setStoredAccessToken } from "./authToken"
import { User } from "@/types/user"
import {
  signInAndGetToken,
  signOut as firebaseSignOut,
} from "@/lib/auth/firebase"
import { mockLogin, mockMe } from "./auth.mock"

<<<<<<< Updated upstream
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true"
const USE_FIREBASE = Boolean(process.env.NEXT_PUBLIC_FIREBASE_API_KEY)

async function loginWithBackend(username: string, password: string): Promise<User> {
  const { data: token } = await apiClient.post<{
    access_token: string
    expires_in?: number
  }>("/auth/login", {
    username,
    password,
  })

  setStoredAccessToken(token.access_token, token.expires_in)

  const { data: me } = await apiClient.get<User>("/auth/me")
  return me
}
=======
import apiClient from "./client";
import { setStoredAccessToken, clearStoredAccessToken } from "./authToken";
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  MeResponse,
  PasswordChangeResponse,
} from "@/types/user";
>>>>>>> Stashed changes

export const authApi = {
  login: async (username: string, password: string): Promise<User> => {
    try {
      return await loginWithBackend(username, password)
    } catch (error) {
      if (USE_MOCK) return mockLogin(username, password)
      if (!USE_FIREBASE) throw error

      await signInAndGetToken(username, password)
      const { data } = await apiClient.get<User>("/auth/me")
      return data
    }
  },

  me: async (): Promise<User> => {
    try {
      const { data } = await apiClient.get<User>("/auth/me")
      return data
    } catch (error) {
      if (USE_MOCK) return mockMe()
      throw error
    }
  },

<<<<<<< Updated upstream
=======
  /** Register a new account. Returns profile directly (no auto-login). */
  register: async (username: string, password: string): Promise<MeResponse> => {
    const payload: RegisterRequest = { username: username.trim(), password };
    const { data } = await apiClient.post<MeResponse>("/auth/register", payload);
    return data;
  },

  changePassword: async (
    currentPassword: string,
    newPassword: string,
  ): Promise<PasswordChangeResponse> => {
    const { data } = await apiClient.post<PasswordChangeResponse>(
      "/auth/change-password",
      { current_password: currentPassword, new_password: newPassword },
    );
    return data;
  },

  /** Logout — clears stored JWT. */
>>>>>>> Stashed changes
  logout: async (): Promise<void> => {
    try {
      await apiClient.post("/auth/logout")
    } finally {
      clearStoredAccessToken()
      if (USE_FIREBASE) await firebaseSignOut()
    }
  },

  changePassword: async (newPassword: string): Promise<void> => {
    const { updatePassword } = await import("firebase/auth")
    const { firebaseAuth } = await import("@/lib/auth/firebase")
    if (!firebaseAuth.currentUser) throw new Error("Not authenticated")
    await updatePassword(firebaseAuth.currentUser, newPassword)
    await apiClient.post("/auth/password-changed")
  },

  register: async (username: string, password: string): Promise<User> => {
    try {
      const { data: user } = await apiClient.post<User>("/auth/register", {
        username,
        password,
      })
      await loginWithBackend(username, password)
      return user
    } catch (error) {
      if (USE_MOCK) return mockLogin(username, password)
      throw error
    }
  },
}
