"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/stores/authStore"
import { authApi } from "@/lib/api/auth"

export function useAuth() {
  const { user, setUser, logout: clearStore } = useAuthStore()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const login = async (username: string, password: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const me = await authApi.login(username, password)
      setUser(me)
      router.push("/dashboard")
    } catch {
      setError("Đăng nhập thất bại. Kiểm tra username, mật khẩu và backend port 8000.")
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (username: string, password: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const me = await authApi.register(username, password)
      setUser(me)
      router.push("/dashboard")
    } catch {
      setError("Đăng ký thất bại. Vui lòng thử lại.")
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } finally {
      clearStore()
      router.push("/login")
    }
  }

  return { user, isLoading, error, login, register, logout }
}
