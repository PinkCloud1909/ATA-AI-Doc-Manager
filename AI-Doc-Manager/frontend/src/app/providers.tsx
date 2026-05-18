"use client"

import { useEffect } from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useState } from "react"
import { Toaster } from "sonner"
import { authApi } from "@/lib/api/auth"
import { clearStoredAccessToken, getStoredAccessToken } from "@/lib/api/authToken"
import { useAuthStore } from "@/stores/authStore"

function BackendSessionSync() {
  const setUser = useAuthStore((s) => s.setUser)
  const logout  = useAuthStore((s) => s.logout)

  useEffect(() => {
    const syncSession = async () => {
      if (!getStoredAccessToken()) {
        logout()
        return
      }

      const storeUser = useAuthStore.getState().user
      if (!storeUser) {
        try {
          const me = await authApi.me()
          setUser(me)
        } catch {
          clearStoredAccessToken()
          logout()
        }
      }
    }

    void syncSession()
  }, [setUser, logout])

  return null
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime:            60_000,
            retry:                1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  )

  return (
    <QueryClientProvider client={queryClient}>
      <BackendSessionSync />
      {children}
      <Toaster richColors position="top-right" />
    </QueryClientProvider>
  )
}
