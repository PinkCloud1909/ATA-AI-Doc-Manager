import { useMemo } from "react"
import { useAuthStore } from "@/stores/authStore"

export function usePermission() {
  const user = useAuthStore((s) => s.user)

  return useMemo(() => {
    if (!user) return { canUpload: false, canReview: false, canApprove: false, canAdmin: false, roleNames: [] as string[] }
    const roleNames = (user.roles ?? []).map((ur) => ur.role?.role_name ?? "")
    return {
      roleNames,
      canUpload:  roleNames.some((r) => ["Admin", "Uploader"].includes(r)),
      canReview:  roleNames.some((r) => ["Admin", "Reviewer"].includes(r)),
      canApprove: roleNames.some((r) => ["Admin", "Reviewer"].includes(r)),
      canAdmin:   roleNames.includes("Admin"),
    }
  }, [user])
}
