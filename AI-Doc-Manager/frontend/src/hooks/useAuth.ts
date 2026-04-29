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
      const code = (err as { code?: string })?.code
      // Firebase error codes
      const MSG: Record<string, string> = {
        "auth/user-not-found":    "Email không tồn tại",
        "auth/wrong-password":    "Mật khẩu không đúng",
        "auth/too-many-requests": "Quá nhiều lần thử. Vui lòng thử lại sau",
        "auth/invalid-email":     "Email không hợp lệ",
      }
      setError(MSG[code ?? ""] ?? "Đăng nhập thất bại")
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
      const code = (err as { code?: string })?.code
      // Firebase registration error codes
      const MSG: Record<string, string> = {
        "auth/email-already-in-use":  "Email này đã được sử dụng",
        "auth/weak-password":         "Mật khẩu quá yếu (Cần ít nhất 6 ký tự)",
        "auth/invalid-email":         "Email không hợp lệ",
        "auth/operation-not-allowed": "Đăng ký bằng email đã bị vô hiệu hóa",
      }
      setError(MSG[code ?? ""] ?? "Đăng ký thất bại. Vui lòng thử lại.")
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