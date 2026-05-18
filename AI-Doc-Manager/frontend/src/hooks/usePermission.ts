import { useMemo } from "react"
import { useAuthStore } from "@/stores/authStore"

export function usePermission() {
  const user = useAuthStore((s) => s.user)

  return useMemo(() => {
    if (!user) return { canUpload: false, canReview: false, canApprove: false, canAdmin: false, roleNames: [] as string[] }
    const roleNames = (user.roles ?? [])
      .map((role) => typeof role === "string" ? role : role.role?.role_name ?? "")
      .filter(Boolean)
    const normalizedRoleNames = roleNames.map((role) => role.toLowerCase())
    return {
      roleNames,
      canUpload:  normalizedRoleNames.some((r) => ["admin", "uploader"].includes(r)),
      canReview:  normalizedRoleNames.some((r) => ["admin", "reviewer"].includes(r)),
      canApprove: normalizedRoleNames.some((r) => ["admin", "reviewer"].includes(r)),
      canAdmin:   normalizedRoleNames.includes("admin"),
    }
  }, [user])
}
