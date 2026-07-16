import { redirect } from "next/navigation"
import { cookies } from "next/headers"

export default async function RootPage() {
  // Server-side: check for auth cookie or just redirect
  // Full auth check happens in (main)/layout.tsx middleware
  const cookieStore = await cookies()
  const hasToken = cookieStore.get("access_token")
  redirect(hasToken ? "/dashboard" : "/login")
  //redirect("/dashboard")
}
