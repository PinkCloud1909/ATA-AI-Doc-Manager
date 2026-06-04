import { useMemo } from "react"
import { useAuthStore } from "@/stores/authStore"

export function usePermission() {
  const user = useAuthStore((s) => s.user)

  return useMemo(() => {
    if (!user) {
      return {
        canUpload: false,
        canReview: false,
        canApprove: false,
        canAdmin: false,
        canExpire: false,
        roleNames: [] as string[],
      }
    }
    const roleNames = (user.roles ?? [])
      .map((ur) => ur.role?.role_name ?? "")
      .filter(Boolean)
    const normalizedRoles = roleNames.map((role) => role.toLowerCase())
    const hasAnyRole = (roles: string[]) =>
      normalizedRoles.some((role) => roles.includes(role))

    return {
      roleNames,
      canUpload: hasAnyRole(["admin", "editor"]),
      canReview: hasAnyRole(["admin", "reviewer"]),
      canApprove: hasAnyRole(["admin", "reviewer"]),
      canExpire: hasAnyRole(["admin", "reviewer"]),
      canAdmin: normalizedRoles.includes("admin"),
    }
  }, [user])
}
