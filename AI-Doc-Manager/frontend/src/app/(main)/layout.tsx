"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/stores/authStore"
import Sidebar from "@/components/layout/Sidebar"
import Header  from "@/components/layout/Header"

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (!isAuthenticated()) router.replace("/login")
  }, [isAuthenticated, router])

  if (!isAuthenticated()) return null

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
