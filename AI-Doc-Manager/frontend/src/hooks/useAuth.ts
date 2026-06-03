"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import axios from "axios"
import { useAuthStore } from "@/stores/authStore"
import { authApi } from "@/lib/api/auth"

interface ApiErrorResponse {
  detail?: string
  code?: string
}

function getAuthErrorMessage(err: unknown, fallback: string) {
  if (!axios.isAxiosError<ApiErrorResponse>(err)) {
    return (err as Error)?.message ?? fallback
  }

  const status = err.response?.status
  const data = err.response?.data

  if (status === 422 && data?.code === "request_validation_error") {
    return "Tên đăng nhập phải có ít nhất 3 ký tự và mật khẩu ít nhất 8 ký tự."
  }

  if (typeof data?.detail === "string") return data.detail

  return err.message || fallback
}

export function useAuth() {
  const { user, setUser, logout: clearStore } = useAuthStore()
  const router    = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError]         = useState<string | null>(null)

  const login = async (username: string, password: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const me = await authApi.login(username, password)
      setUser(me)
      router.push("/dashboard")
    } catch (err: unknown) {
      setError(getAuthErrorMessage(err, "Đăng nhập thất bại"))
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
    } catch (err: unknown) {
      setError(getAuthErrorMessage(err, "Đăng ký thất bại. Vui lòng thử lại."))
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
