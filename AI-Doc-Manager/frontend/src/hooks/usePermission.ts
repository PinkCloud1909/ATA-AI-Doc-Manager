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
        roleNames: [] as string[],
      }
    }

    const roleNames = [
      ...(user.roles ?? [])
        .map((role) =>
          typeof role === "string" ? role : role.role?.role_name ?? "",
        ),
      user.role ?? "",
    ].filter(Boolean)
    const normalizedRoleNames = roleNames.map((role) => role.toLowerCase())
    const normalizedPermissions = (user.permissions ?? []).map((permission) =>
      permission.toLowerCase(),
    )
    const hasRole = (...roles: string[]) =>
      normalizedRoleNames.some((role) => roles.includes(role))
    const hasPermission = (...permissions: string[]) =>
      normalizedPermissions.some((permission) => permissions.includes(permission))

    return {
      roleNames,
      canUpload:
        hasRole("admin", "uploader", "editor") ||
        hasPermission("write", "upload", "post:/api/v1/documents/upload"),
      canReview:
        hasRole("admin", "reviewer", "approver") ||
        hasPermission("review", "get:/api/v1/approvals/pending"),
      canApprove:
        hasRole("admin", "reviewer", "approver") ||
        hasPermission("approve", "post:/api/v1/documents/{document_id}/approve"),
      canAdmin:
        hasRole("admin") ||
        hasPermission("manage_users", "get:/api/v1/admin/users"),
    }
  }, [user])
}
