"use client"

import { useEffect } from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useState } from "react"
import { Toaster } from "sonner"
import { onTokenRefresh } from "@/lib/auth/firebase"
import { authApi } from "@/lib/api/auth"
import { useAuthStore } from "@/stores/authStore"

function FirebaseSessionSync() {
  const setUser = useAuthStore((s) => s.setUser)
  const logout  = useAuthStore((s) => s.logout)

  useEffect(() => {
    // Lắng nghe Firebase ID Token thay đổi:
    //  - user = null → đã sign out → clear store
    //  - user != null → token mới → re-fetch profile (nếu cần)
    const unsubscribe = onTokenRefresh(async (firebaseUser) => {
      if (!firebaseUser) {
        logout()
        return
      }
      // Nếu store chưa có user (e.g. reload trang), fetch profile
      const storeUser = useAuthStore.getState().user
      if (!storeUser) {
        try {
          const me = await authApi.me()
          setUser(me)
        } catch {
          logout()
        }
      }
    })

    return unsubscribe
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
      <FirebaseSessionSync />
      {children}
      <Toaster richColors position="top-right" />
    </QueryClientProvider>
  )
}
