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

// Use || (not ??) so that an empty string "" also falls back to the relative
// path.  An empty string happens when the Docker build does not receive the
// NEXT_PUBLIC_API_URL build-arg (the Dockerfile's `ENV VAR=$VAR` copies the
// empty arg literally, which ??. treats as "set").
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api/v1"

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
