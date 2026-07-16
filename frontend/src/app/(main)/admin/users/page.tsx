"use client";

import { useMemo, useState } from "react";
import { useAdminUsers, useAdminRoles, useCreateUser, useAssignRole, useRemoveRole } from "@/hooks/useAdmin";
import { useTranslation, formatT } from "@/i18n/LanguageContext";
import { toast } from "sonner";
import { getApiErrorMessage } from "@/lib/error-handler";

type UserRole = "admin" | "viewer" | "editor" | "reviewer" | "All";

const roleDots: Record<string, string> = {
  admin: "bg-tertiary",
  viewer: "bg-outline-variant",
  editor: "bg-secondary-dim",
  reviewer: "bg-tertiary",
};

const rolePermissions: Array<{ role: string; permissions: string }> = [
  { role: "admin", permissions: "Full system access: manage users, roles, all documents." },
  { role: "viewer", permissions: "View approved documents only." },
  { role: "editor", permissions: "Upload documents, edit, submit for review." },
  { role: "reviewer", permissions: "View approval queue, approve/reject documents, grade." },
];

function StatCard({ label, value, dotClass }: { label: string; value: number; dotClass?: string }) {
  return (
    <section className="border border-outline-variant/10 bg-white p-6 shadow-sm">
      <div className="mb-8 flex items-center gap-3">
        {dotClass && <span className={`h-2.5 w-2.5 rounded-full ${dotClass}`} />}
        <p className="text-sm font-bold uppercase tracking-wide text-on-surface-variant">{label}</p>
      </div>
      <p className="text-4xl font-black tracking-tight text-on-surface">
        {value.toLocaleString("en-US")}
      </p>
    </section>
  );
}

export default function UsersPage() {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState<UserRole>("All");
  const [isPermissionsOpen, setIsPermissionsOpen] = useState(false);
  const [roleDropdownUser, setRoleDropdownUser] = useState<string | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const { data: usersData, isLoading, error } = useAdminUsers({ page_size: 200 });
  const { data: rolesList } = useAdminRoles();
  const createUser = useCreateUser();
  const assignRole = useAssignRole();
  const removeRole = useRemoveRole();

  const users = usersData?.items ?? [];

  const handleAssignRole = async (userId: string, roleName: string) => {
    try {
      await assignRole.mutateAsync({ userId, roleName });
      toast.success(t.admin.roleAssigned);
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Failed to assign role"));
    }
    setRoleDropdownUser(null);
  };

  const handleRemoveRole = async (userId: string, roleName: string) => {
    try {
      await removeRole.mutateAsync({ userId, roleName });
      toast.success(t.admin.roleRemoved);
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Failed to remove role"));
    }
  };

  const handleCreateUser = async () => {
    try {
      await createUser.mutateAsync({
        username: newUsername.trim(),
        password: newPassword,
      });
      toast.success(t.admin.userCreated ?? "User created");
      setIsCreateOpen(false);
      setNewUsername("");
      setNewPassword("");
    } catch (err) {
      toast.error(getApiErrorMessage(err));
    }
  };

  const roleCounts = useMemo(() => {
    const counts: Record<string, number> = { admin: 0, viewer: 0, editor: 0, reviewer: 0 };
    for (const u of users) {
      for (const role of u.roles) {
        const normalized = role.toLowerCase();
        if (normalized in counts) counts[normalized] = (counts[normalized] ?? 0) + 1;
      }
    }
    return counts;
  }, [users]);

  const displayedUsers = useMemo(() => {
    const normalizedQuery = searchQuery.trim().toLowerCase();
    return users.filter((user) => {
      const matchesSearch =
        !normalizedQuery || user.username.toLowerCase().includes(normalizedQuery);
      const userRoles = user.roles.map((r) => r.toLowerCase());
      const matchesRole = roleFilter === "All" || userRoles.includes(roleFilter.toLowerCase());
      return matchesSearch && matchesRole;
    });
  }, [users, searchQuery, roleFilter]);

  const getInitials = (username: string) => username.slice(0, 2).toUpperCase();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-3 border-tertiary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <span className="material-symbols-outlined text-4xl text-error">error</span>
        <p className="text-sm text-on-surface-variant">{t.errors.cannotLoadUsers}</p>
        <button onClick={() => window.location.reload()} className="text-sm text-tertiary font-semibold">
          {t.common.retry}
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-8 md:px-8">
      <div className="mb-12">
        <h1 className="text-4xl font-black tracking-tight text-on-surface md:text-5xl">
          {t.admin.title}
        </h1>
        <p className="mt-4 text-lg text-on-surface-variant">{t.admin.subtitle}</p>
      </div>

      <div className="mb-12 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label={t.admin.totalUsers} value={users.length} />
        <StatCard label="Admin" value={roleCounts.admin ?? 0} dotClass={roleDots.admin} />
        <StatCard label="Editor" value={roleCounts.editor ?? 0} dotClass={roleDots.editor} />
        <StatCard label="Reviewer" value={roleCounts.reviewer ?? 0} dotClass={roleDots.reviewer} />
      </div>

      <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-col gap-4 sm:flex-row">
          <label className="flex h-12 w-full items-center gap-3 bg-surface-container-low px-4 text-on-surface-variant sm:w-[420px]">
            <span className="material-symbols-outlined text-[22px]">search</span>
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full border-none bg-transparent text-base text-on-surface placeholder:text-on-surface-variant focus:ring-0"
              placeholder={t.admin.searchPlaceholder}
              type="search"
            />
          </label>
          <label className="relative h-12 min-w-48 bg-surface-container-low">
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value as UserRole)}
              className="h-full w-full appearance-none border-none bg-transparent px-5 pr-11 text-base font-medium text-on-surface focus:ring-0"
            >
              <option value="All">{t.admin.allRoles}</option>
              <option value="admin">Admin</option>
              <option value="editor">Editor</option>
              <option value="reviewer">Reviewer</option>
              <option value="viewer">Viewer</option>
            </select>
            <span className="material-symbols-outlined pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-[22px] text-on-surface-variant">
              expand_more
            </span>
          </label>
        </div>
        <button
          type="button"
          onClick={() => setIsPermissionsOpen(true)}
          className="inline-flex h-12 items-center justify-center gap-3 bg-surface-container px-6 text-sm font-bold text-on-surface shadow-sm hover:bg-surface-container-high"
        >
          <span className="material-symbols-outlined text-[21px]">policy</span>
          {t.admin.viewPermissions}
        </button>
        <button
          type="button"
          onClick={() => setIsCreateOpen(true)}
          className="inline-flex h-12 items-center justify-center gap-3 bg-tertiary px-6 text-sm font-bold text-on-tertiary shadow-sm hover:bg-tertiary-dim"
        >
          <span className="material-symbols-outlined text-[21px]">person_add</span>
          {t.admin.createUser ?? "Create User"}
        </button>
      </div>

      <section className="overflow-hidden border border-outline-variant/10 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px] text-left">
            <thead className="border-b border-outline-variant/10 bg-surface-bright text-sm uppercase tracking-wide text-on-surface-variant">
              <tr>
                <th className="px-4 py-6 font-bold">{t.admin.user}</th>
                <th className="px-4 py-6 font-bold">{t.admin.role}</th>
                <th className="px-4 py-6 font-bold">{t.common.status}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {displayedUsers.length === 0 ? (
                <tr>
                  <td colSpan={3} className="px-8 py-12 text-center text-sm text-on-surface-variant">
                    {users.length === 0 ? t.admin.noUsers : t.admin.noUsersFound}
                  </td>
                </tr>
              ) : (
                displayedUsers.map((user) => (
                  <tr key={user.id} className="transition-colors hover:bg-surface-bright">
                    <td className="px-4 py-5">
                      <div className="flex items-center gap-4">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary-container text-sm font-bold text-on-secondary-container">
                          {getInitials(user.username)}
                        </div>
                        <span className="max-w-44 text-base font-semibold text-on-surface">
                          {user.username}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-5">
                      <div className="flex flex-wrap items-center gap-1">
                        {user.roles.map((roleName, idx) => {
                          const normalizedRole = roleName.toLowerCase();
                          return (
                            <span key={idx} className="inline-flex items-center gap-1 min-w-20 justify-center rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wide bg-surface-container-low text-on-surface-variant">
                              {roleName}
                              <button
                                type="button"
                                onClick={() => handleRemoveRole(user.id, normalizedRole)}
                                className="ml-0.5 inline-flex items-center justify-center w-3.5 h-3.5 rounded-full hover:bg-error/20 hover:text-error transition-colors"
                                aria-label={t.admin.removeRole}
                              >
                                <span className="material-symbols-outlined text-[12px]">close</span>
                              </button>
                            </span>
                          );
                        })}
                        {user.roles.length === 0 && (
                          <span className="text-xs text-on-surface-variant">—</span>
                        )}
                        <div className="relative inline-flex">
                          <button
                            type="button"
                            onClick={() => setRoleDropdownUser(roleDropdownUser === user.id ? null : user.id)}
                            className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-surface-container-high text-on-surface-variant hover:bg-tertiary-container hover:text-tertiary transition-colors"
                            aria-label={t.admin.assignRole}
                          >
                            <span className="material-symbols-outlined text-[16px]">add</span>
                          </button>
                          {roleDropdownUser === user.id && (
                            <div className="absolute left-0 top-full mt-1 z-50 min-w-40 bg-white border border-outline-variant/20 rounded-lg shadow-lg py-1">
                              {(rolesList ?? []).filter((r) => !user.roles.some((ur) => ur.toLowerCase() === r.role_name.toLowerCase())).map((r) => (
                                <button
                                  key={r.id}
                                  type="button"
                                  onClick={() => handleAssignRole(user.id, r.role_name)}
                                  className="block w-full text-left px-4 py-2 text-sm text-on-surface hover:bg-surface-container-low transition-colors"
                                >
                                  {r.role_name}
                                </button>
                              ))}
                              {(rolesList ?? []).filter((r) => !user.roles.some((ur) => ur.toLowerCase() === r.role_name.toLowerCase())).length === 0 && (
                                <span className="block px-4 py-2 text-sm text-on-surface-variant">All roles assigned</span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-5">
                      <span className="inline-flex items-center gap-2 text-sm font-medium text-on-surface">
                        <span className="h-2 w-2 rounded-full bg-emerald-500" />
                        {t.admin.active}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <div className="flex flex-col gap-4 border-t border-outline-variant/10 px-8 py-6 text-base text-on-surface-variant sm:flex-row sm:items-center sm:justify-between">
          <span>
            {formatT(t.admin.showingUsers, { displayed: displayedUsers.length, total: users.length })}
          </span>
        </div>
      </section>

      {/* Permissions Modal */}
      {isPermissionsOpen && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center bg-black/35 p-4 backdrop-blur-sm" role="dialog" aria-modal="true">
          <div className="w-full max-w-xl overflow-hidden bg-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-outline-variant/10 px-8 py-6">
              <h2 className="text-2xl font-black tracking-tight text-on-surface">{t.admin.permissionsTitle}</h2>
              <button type="button" onClick={() => setIsPermissionsOpen(false)} className="material-symbols-outlined p-1 text-[28px] text-on-surface-variant hover:text-on-surface">close</button>
            </div>
            <div className="px-8 py-7">
              <div className="space-y-7">
                {rolePermissions.map((item) => (
                  <div key={item.role} className="flex gap-5">
                    <span className={`mt-2 h-2.5 w-2.5 shrink-0 rounded-full ${roleDots[item.role] ?? "bg-outline-variant"}`} />
                    <div>
                      <p className="text-base font-black uppercase tracking-wide text-on-surface">{item.role}</p>
                      <p className="mt-2 text-base leading-6 text-on-surface-variant">{item.permissions}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex justify-end bg-surface-container-low px-8 py-5">
              <button type="button" onClick={() => setIsPermissionsOpen(false)} className="bg-surface-container px-6 py-3 text-sm font-bold text-on-surface hover:bg-surface-container-high">{t.common.close}</button>
            </div>
          </div>
        </div>
      )}

      {/* Create User Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center bg-black/35 p-4 backdrop-blur-sm" role="dialog" aria-modal="true">
          <form
            onSubmit={(e) => { e.preventDefault(); handleCreateUser(); }}
            className="w-full max-w-md overflow-hidden bg-white shadow-2xl"
          >
            <div className="flex items-center justify-between border-b border-outline-variant/10 px-8 py-6">
              <h2 className="text-2xl font-black tracking-tight text-on-surface">{t.admin.createUser ?? "Create User"}</h2>
              <button type="button" onClick={() => setIsCreateOpen(false)} className="material-symbols-outlined p-1 text-[28px] text-on-surface-variant hover:text-on-surface">close</button>
            </div>
            <div className="px-8 py-7 space-y-5">
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-on-surface">{t.admin.user}</label>
                <input
                  type="text" required minLength={3} value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  className="w-full bg-surface-container-lowest border-none ring-1 ring-inset ring-outline-variant/40 focus:ring-2 focus:ring-inset focus:ring-tertiary rounded-lg px-3 py-2.5 text-sm"
                  placeholder={t.admin.searchPlaceholder}
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-on-surface">Password</label>
                <input
                  type="password" required minLength={8} value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full bg-surface-container-lowest border-none ring-1 ring-inset ring-outline-variant/40 focus:ring-2 focus:ring-inset focus:ring-tertiary rounded-lg px-3 py-2.5 text-sm"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 bg-surface-container-low px-8 py-5">
              <button type="button" onClick={() => setIsCreateOpen(false)} className="bg-surface-container px-6 py-3 text-sm font-bold text-on-surface hover:bg-surface-container-high">{t.common.cancel}</button>
              <button type="submit" disabled={createUser.isPending} className="bg-tertiary px-6 py-3 text-sm font-bold text-on-tertiary hover:bg-tertiary-dim disabled:opacity-60">
                {createUser.isPending ? t.common.loading : (t.admin.createUser ?? "Create")}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
