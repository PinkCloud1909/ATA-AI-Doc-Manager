/**
 * lib/api/client.ts
 *
 * Axios instance với Firebase ID Token authentication.
 *
 * Khác với kiến trúc cũ (MinIO + custom JWT):
 *  - Token là Firebase ID Token (Google-issued, verify phía backend qua IAM)
 *  - Không cần refresh endpoint riêng → Firebase SDK tự rotate token
 *  - Khi token hết hạn, getCurrentIdToken() tự lấy token mới
 */

import axios, {
  AxiosError,
  InternalAxiosRequestConfig,
} from "axios"
import { getCurrentIdToken } from "@/lib/auth/firebase"

// Mock mode: dùng local Next.js API routes thay vì backend thật
// Khi cần kết nối backend, set NEXT_PUBLIC_USE_MOCK=false
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK !== "false"

const BASE_URL = USE_MOCK
  ? "" // Dùng relative URL → Next.js sẽ proxy đến /api/... local
  : process.env.NEXT_PUBLIC_API_URL ?? "/api/v1"

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 60_000,  // Cloud Run cold start có thể chậm hơn local
})

// ── Request interceptor: đính Firebase ID Token ───────────────────────────────
apiClient.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  const token = await getCurrentIdToken()
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response interceptor: xử lý 401 ─────────────────────────────────────────
apiClient.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Firebase token hết hạn hoặc bị revoke
      // Redirect về login để user đăng nhập lại
      if (typeof window !== "undefined") {
        window.location.href = "/login"
      }
    }
    return Promise.reject(error)
  },
)

export default apiClient
