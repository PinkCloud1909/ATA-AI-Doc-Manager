const ACCESS_TOKEN_KEY = "access_token"

export function getStoredAccessToken(): string | null {
  if (typeof window === "undefined") return null
  return window.localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function setStoredAccessToken(token: string, maxAgeSeconds?: number): void {
  if (typeof window === "undefined") return

  window.localStorage.setItem(ACCESS_TOKEN_KEY, token)

  const maxAge = maxAgeSeconds ? `; Max-Age=${maxAgeSeconds}` : ""
  document.cookie = `${ACCESS_TOKEN_KEY}=${encodeURIComponent(token)}; Path=/; SameSite=Lax${maxAge}`
}

export function clearStoredAccessToken(): void {
  if (typeof window === "undefined") return

  window.localStorage.removeItem(ACCESS_TOKEN_KEY)
  document.cookie = `${ACCESS_TOKEN_KEY}=; Path=/; SameSite=Lax; Max-Age=0`
}
