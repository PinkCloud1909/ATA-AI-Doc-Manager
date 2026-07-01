"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/stores/authStore"
import { authApi } from "@/lib/api/auth"
import Sidebar from "@/components/layout/Sidebar"
import Header  from "@/components/layout/Header"

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const { user, logout: clearStore } = useAuthStore()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const [verified, setVerified] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return
    if (!user) {
      setVerified(false)
      router.replace("/login")
      return
    }

    let cancelled = false
    setVerified(false)
    authApi.me()
      .then(() => {
        if (!cancelled) setVerified(true)
      })
      .catch(() => {
        if (!cancelled) {
          clearStore()
          router.replace("/login")
        }
      })

    return () => {
      cancelled = true
    }
  }, [clearStore, mounted, router, user])

  if (!mounted || !user || !verified) return null

  return (
    <div className="flex h-[100vh] w-[100vw] overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 h-full overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
