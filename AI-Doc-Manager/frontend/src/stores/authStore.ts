"use client"

/**
 * stores/authStore.ts
 *
 * Với Firebase Auth:
 *  - Không lưu access_token thủ công (Firebase SDK quản lý)
 *  - Chỉ lưu User profile (roles, permissions) từ backend PostgreSQL
 *  - Firebase session tồn tại trong IndexedDB (Firebase persistence)
 */

import { create } from "zustand"
import { persist } from "zustand/middleware"
import { User } from "@/types/user"

interface AuthState {
  // Profile từ backend PostgreSQL (roles, permissions)
  user: User | null

  // Actions
  setUser:  (user: User | null) => void
  logout:   () => void
  isAuthenticated: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,

      setUser: (user) => set({ user }),

      logout: () => set({ user: null }),

      isAuthenticated: () => Boolean(get().user),
    }),
    {
      name:        "auth-user",
      partialize:  (s) => ({ user: s.user }),
    },
  ),
)
