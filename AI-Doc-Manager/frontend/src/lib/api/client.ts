import axios, { AxiosError, InternalAxiosRequestConfig } from "axios"
import { getCurrentIdToken } from "@/lib/auth/firebase"
import {
  clearStoredAccessToken,
  getStoredAccessToken,
  setStoredAccessToken,
} from "./authToken"

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1"

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 60_000,
})

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

async function getDevAccessToken(): Promise<string | null> {
  if (typeof window === "undefined") return null
  const { data } = await axios.post(`${BASE_URL}/auth/login`, {
    username: "admin",
    password: "admin123",
  })
  const token = data?.access_token as string | undefined
  if (token) setStoredAccessToken(token, data?.expires_in)
  return token ?? null
}

apiClient.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  let token = getStoredAccessToken() || await getCurrentIdToken()
  if (!token) token = await getDevAccessToken()

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
      const token = await getDevAccessToken()

      if (token) {
        originalRequest.headers.Authorization = `Bearer ${token}`
        return apiClient(originalRequest)
      }
    }

    return Promise.reject(error)
  },
)

export default apiClient
