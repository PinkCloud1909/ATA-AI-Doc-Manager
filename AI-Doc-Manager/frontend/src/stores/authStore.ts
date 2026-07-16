"use client";

/**
 * stores/authStore.ts
 *
 * JWT-based auth via backend. Stores the user profile from GET /api/v1/auth/me.
 * JWT is managed separately in lib/api/authToken.ts (localStorage + cookie).
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { MeResponse } from "@/types/user";

interface AuthState {
  user: MeResponse | null;
  setUser: (user: MeResponse | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,

      setUser: (user) => set({ user }),

      logout: () => set({ user: null }),
    }),
    {
      name: "auth-user",
      partialize: (s) => ({ user: s.user }),
    },
  ),
);
