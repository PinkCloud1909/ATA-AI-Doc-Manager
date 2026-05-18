/**
 * lib/api/client.ts
 *
 * Axios instance dùng JWT do FastAPI backend cấp qua /api/v1/auth/login.
 */

import axios, {
  AxiosError,
  InternalAxiosRequestConfig,
} from "axios"
import { clearStoredAccessToken, getStoredAccessToken } from "./authToken"

// Mock mode: dùng local Next.js API routes thay vì backend thật.
// Mặc định gọi backend; chỉ bật mock khi NEXT_PUBLIC_USE_MOCK=true.
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true"

const BASE_URL = USE_MOCK
  ? "" // Dùng relative URL → Next.js sẽ proxy đến /api/... local
  : process.env.NEXT_PUBLIC_API_URL ?? "/api/v1"

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 60_000,  // Cloud Run cold start có thể chậm hơn local
})

// ── Request interceptor: đính backend JWT ───────────────────────────────────
apiClient.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  const token = getStoredAccessToken()
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
      clearStoredAccessToken()
      if (typeof window !== "undefined") {
        const isAuthPage = ["/login", "/register"].includes(window.location.pathname)
        if (!isAuthPage) window.location.href = "/login"
      }
    }
    return Promise.reject(error)
  },
)

export default apiClient
