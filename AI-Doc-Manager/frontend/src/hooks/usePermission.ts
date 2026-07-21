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
<<<<<<< Updated upstream
=======
        canComment: false,
        canViewReviews: false,
        canViewRag: false,
        canManageRag: false,
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
      roleNames,
      canUpload: hasAnyRole(["admin", "editor"]),
      canReview: hasAnyRole(["admin", "reviewer"]),
      canApprove: hasAnyRole(["admin", "reviewer"]),
      canExpire: hasAnyRole(["admin", "reviewer"]),
      canAdmin: normalizedRoles.includes("admin"),
    }
  }, [user])
=======
      roleNames: user.roles ?? [],
      canUpload:
        hasRole("admin", "editor") ||
        hasPermission("post:/api/v1/documents/upload"),
      canReview:
        hasRole("admin", "reviewer") ||
        hasPermission("get:/api/v1/approvals/pending"),
      canApprove:
        hasRole("admin", "reviewer") ||
        hasPermission("post:/api/v1/documents/{document_id}/approve"),
      canAdmin:
        hasRole("admin") ||
        hasPermission("get:/api/v1/admin/users"),
      canComment:
        hasRole("admin", "reviewer", "viewer") ||
        hasPermission("post:/api/v1/documents/{document_id}/reviews"),
      canViewReviews:
        hasRole("admin", "reviewer", "viewer", "editor") ||
        hasPermission("get:/api/v1/documents/{document_id}/reviews"),
      canViewRag:
        hasRole("admin", "reviewer", "viewer", "editor") ||
        hasPermission("get:/api/v1/rag/{document_id}/status"),
      canManageRag:
        hasPermission(
          "post:/api/v1/rag/{document_id}",
          "delete:/api/v1/rag/{document_id}",
        ),
      canExpire:
        hasRole("admin", "reviewer") ||
        hasPermission("post:/api/v1/documents/{document_id}/expire"),
    };
  }, [user]);
>>>>>>> Stashed changes
}
