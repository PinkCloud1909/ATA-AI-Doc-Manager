import { useMemo } from "react";
import { useAuthStore } from "@/stores/authStore";

export function usePermission() {
  const user = useAuthStore((s) => s.user);

  return useMemo(() => {
    if (!user) {
      return {
        canUpload: false,
        canReview: false,
        canApprove: false,
        canAdmin: false,
        roleNames: [] as string[],
      };
    }

    // API returns roles and permissions as flat string arrays
    const roles = (user.roles ?? []).map((r) => r.toLowerCase());
    const perms = (user.permissions ?? []).map((p) => p.toLowerCase());

    const hasRole = (...targets: string[]) =>
      targets.some((t) => roles.includes(t));
    const hasPermission = (...targets: string[]) =>
      targets.some((t) => perms.includes(t));

    return {
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
    };
  }, [user]);
}
