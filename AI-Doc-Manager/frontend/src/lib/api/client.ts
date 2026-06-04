import axios, { AxiosError, InternalAxiosRequestConfig } from "axios"
import { getCurrentIdToken } from "@/lib/auth/firebase"
import {
  clearStoredAccessToken,
  getStoredAccessToken,
} from "./authToken"

const BASE_URL =
  typeof window !== "undefined"
    ? "/api/v1"
    : process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1"

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 60_000,
})

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

apiClient.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  const url = config.url ?? ""
  if (url.includes("/auth/login") || url.includes("/auth/register")) {
    return config
  }

  const token = getStoredAccessToken() || await getCurrentIdToken()

  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined

    if (
      error.response?.status === 401 &&
      typeof window !== "undefined" &&
      originalRequest &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true
      clearStoredAccessToken()
    }

    return Promise.reject(error)
  },
)

export default apiClient
