"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { useAuthStore } from "@/stores/authStore";
import { authApi } from "@/lib/api/auth";

function getAuthErrorMessage(err: unknown, fallback: string): string {
  if (!axios.isAxiosError(err)) {
    return (err as Error)?.message ?? fallback;
  }
  const data = err.response?.data as { detail?: string } | undefined;
  if (typeof data?.detail === "string") return data.detail;
  return err.message || fallback;
}

export function useAuth() {
  const { user, setUser, logout: clearStore } = useAuthStore();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      await authApi.login(username, password);
      const me = await authApi.me();
      setUser(me);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(getAuthErrorMessage(err, "Đăng nhập thất bại"));
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      await authApi.register(username, password);
      // After registration, log in to get JWT and full profile
      await authApi.login(username, password);
      const me = await authApi.me();
      setUser(me);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(getAuthErrorMessage(err, "Đăng ký thất bại. Vui lòng thử lại."));
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } finally {
      clearStore();
      router.push("/login");
    }
  };

  return { user, isLoading, error, login, register, logout };
}
