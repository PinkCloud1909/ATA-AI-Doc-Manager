"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/stores/authStore"
import { authApi } from "@/lib/api/auth"

export function useAuth() {
  const { user, setUser, logout: clearStore } = useAuthStore()
  const router    = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError]         = useState<string | null>(null)

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    setError(null)
    try {
      // authApi.login: Firebase signIn → lấy profile từ backend
      const me = await authApi.login(email, password)
      setUser(me)
      router.push("/dashboard")
    } catch (err: unknown) {
      const message = (err as Error)?.message
      setError(message ?? "Đăng nhập thất bại")
    } finally {
      setIsLoading(false)
    }
  }

  // === BỔ SUNG HÀM REGISTER ===
  const register = async (email: string, password: string) => {
    setIsLoading(true)
    setError(null)
    try {
      // authApi.register: Firebase createUserWithEmailAndPassword → tạo profile từ backend
      const me = await authApi.register(email, password)
      
      // Tự động đăng nhập sau khi đăng ký thành công
      setUser(me)
      router.push("/dashboard")
    } catch (err: unknown) {
      const message = (err as Error)?.message
      setError(message ?? "Đăng ký thất bại. Vui lòng thử lại.")
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

  // Đừng quên export register ra ngoài nhé!
  return { user, isLoading, error, login, register, logout }
}