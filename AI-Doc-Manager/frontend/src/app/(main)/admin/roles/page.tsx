"use client";

import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api/admin";
import { useTranslation } from "@/i18n/LanguageContext";

export default function AdminRolesPage() {
  const { t } = useTranslation();
  const { data: roles, isLoading } = useQuery({
    queryKey: ["admin", "roles"],
    queryFn: () => adminApi.listRoles(),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-3 border-tertiary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-5xl px-4 py-8 md:px-8">
      <div className="mb-10">
        <h1 className="text-4xl font-black tracking-tight text-on-surface md:text-5xl">
          {t.admin.rolesList}
        </h1>
        <p className="mt-4 text-lg text-on-surface-variant">
          {t.admin.rolesDescription}
        </p>
      </div>

      <section className="overflow-hidden border border-outline-variant/10 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[600px] text-left">
            <thead className="border-b border-outline-variant/10 bg-surface-bright text-sm uppercase tracking-wide text-on-surface-variant">
              <tr>
                <th className="px-6 py-5 font-bold">{t.admin.role}</th>
                <th className="px-6 py-5 font-bold">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {roles && roles.length > 0 ? (
                roles.map((role) => (
                  <tr key={role.id} className="transition-colors hover:bg-surface-bright">
                    <td className="px-6 py-5 text-base font-semibold text-on-surface">
                      {role.role_name}
                    </td>
                    <td className="px-6 py-5 text-base text-on-surface-variant">
                      {role.description || "—"}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={2} className="px-6 py-12 text-center text-sm text-on-surface-variant">
                    {t.common.noResults}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
