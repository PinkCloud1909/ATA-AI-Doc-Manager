"use client"

<<<<<<< Updated upstream
import { FormEvent, useMemo, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ShieldCheck, UserPlus } from "lucide-react"
import { toast } from "sonner"
import { adminApi } from "@/lib/api/admin"

function roleNamesOf(user: { roles?: { role?: { role_name?: string } }[] }) {
  return (user.roles ?? [])
    .map((userRole) => userRole.role?.role_name)
    .filter(Boolean) as string[]
}

export default function UsersPage() {
  const queryClient = useQueryClient()
  const { data: roles = [], isLoading: isLoadingRoles } = useQuery({
    queryKey: ["admin", "roles"],
    queryFn: adminApi.listRoles,
  })
  const { data: users = [], isLoading: isLoadingUsers } = useQuery({
    queryKey: ["admin", "users"],
    queryFn: adminApi.listUsers,
  })

  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [newUserRoles, setNewUserRoles] = useState<string[]>(["viewer"])
  const [roleDrafts, setRoleDrafts] = useState<Record<string, string[]>>({})

  const assignableRoles = useMemo(
    () => roles.filter((role) => role.role_name !== "user"),
    [roles],
  )
=======
import { useMemo, useState } from "react";
import { useAdminUsers, useAdminRoles, useCreateUser, useAssignRole, useRemoveRole, useResetPassword } from "@/hooks/useAdmin";
import { useTranslation, formatT } from "@/i18n/LanguageContext";
import { toast } from "sonner";
import { getApiErrorMessage } from "@/lib/error-handler";
import { getPasswordPolicyChecks, validatePassword } from "@/lib/validation";
import type { UserResponse } from "@/types/user";

type UserRole = "admin" | "viewer" | "editor" | "reviewer" | "All";

const roleDots: Record<string, string> = {
  admin: "bg-tertiary",
  viewer: "bg-outline-variant",
  editor: "bg-secondary-dim",
  reviewer: "bg-tertiary",
};

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
  const [permissionUser, setPermissionUser] = useState<UserResponse | null>(null);
  const [roleDropdownUser, setRoleDropdownUser] = useState<string | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [resetUser, setResetUser] = useState<UserResponse | null>(null);
  const [resetPassword, setResetPassword] = useState("");

  const { data: usersData, isLoading, error } = useAdminUsers({ page_size: 200 });
  const { data: rolesList } = useAdminRoles();
  const createUser = useCreateUser();
  const assignRole = useAssignRole();
  const removeRole = useRemoveRole();
  const resetPasswordMutation = useResetPassword();

  const users = useMemo(() => usersData?.items ?? [], [usersData?.items]);
>>>>>>> Stashed changes

  const userRoleDefaults = useMemo(
    () =>
      Object.fromEntries(users.map((user) => [user.id, roleNamesOf(user)])),
    [users],
  )

  const createUser = useMutation({
    mutationFn: adminApi.createUser,
    onSuccess: () => {
      toast.success("Da tao user")
      setUsername("")
      setPassword("")
      setNewUserRoles(["viewer"])
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] })
    },
    onError: () => toast.error("Khong tao duoc user"),
  })

  const assignRoles = useMutation({
    mutationFn: ({ userId, roles }: { userId: string; roles: string[] }) =>
      adminApi.assignRoles(userId, roles),
    onSuccess: () => {
      toast.success("Da cap nhat role")
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] })
    },
    onError: () => toast.error("Khong cap nhat duoc role"),
  })

  const toggleRole = (
    value: string,
    selectedRoles: string[],
    onChange: (next: string[]) => void,
  ) => {
    if (selectedRoles.includes(value)) {
      onChange(selectedRoles.filter((roleName) => roleName !== value))
      return
    }
<<<<<<< Updated upstream
    onChange([...selectedRoles, value])
=======
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
    const passwordError = validatePassword(newPassword);
    if (passwordError) {
      toast.error(passwordError);
      return;
    }
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

  const handleResetPassword = async () => {
    if (!resetUser) return;
    const passwordError = validatePassword(resetPassword);
    if (passwordError) {
      toast.error(passwordError);
      return;
    }
    try {
      await resetPasswordMutation.mutateAsync({
        userId: resetUser.id,
        newPassword: resetPassword,
      });
      toast.success("Password reset successfully");
      setResetUser(null);
      setResetPassword("");
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Failed to reset password"));
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
>>>>>>> Stashed changes
  }

  const submitCreateUser = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    createUser.mutate({
      username,
      password,
      role_names: newUserRoles.length ? newUserRoles : ["viewer"],
    })
  }

  return (
    <main className="h-full overflow-y-auto p-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Quan ly user</h1>
          <p className="mt-1 text-sm text-slate-500">
            Tao user va gan role Viewer, Editor, Reviewer hoac Admin.
          </p>
        </div>

        <form
          onSubmit={submitCreateUser}
          className="grid gap-4 rounded-lg border border-slate-200 bg-white p-5 lg:grid-cols-[1fr_1fr_1.4fr_auto]"
        >
          <label className="space-y-1 text-sm font-medium text-slate-700">
            Username
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              minLength={3}
              required
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500"
              placeholder="editor01"
            />
          </label>
          <label className="space-y-1 text-sm font-medium text-slate-700">
            Password
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={8}
              required
              type="password"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500"
              placeholder="It nhat 8 ky tu"
            />
          </label>
<<<<<<< Updated upstream
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-700">Role</p>
            <div className="flex flex-wrap gap-2">
              {assignableRoles.map((role) => (
                <label
                  key={role.id}
                  className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700"
                >
                  <input
                    type="checkbox"
                    checked={newUserRoles.includes(role.role_name)}
                    onChange={() =>
                      toggleRole(role.role_name, newUserRoles, setNewUserRoles)
                    }
                  />
                  {role.role_name}
                </label>
              ))}
=======
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
                <th className="px-4 py-6 font-bold">Permissions</th>
                <th className="px-4 py-6 font-bold">{t.admin.role}</th>
                <th className="px-4 py-6 font-bold">Actions</th>
                <th className="px-4 py-6 font-bold">{t.common.status}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {displayedUsers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-8 py-12 text-center text-sm text-on-surface-variant">
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
                      <button
                        type="button"
                        onClick={() => {
                          setPermissionUser(user);
                          setIsPermissionsOpen(true);
                        }}
                        className="inline-flex items-center gap-1.5 text-sm font-semibold text-tertiary hover:underline"
                      >
                        <span className="material-symbols-outlined text-[17px]">policy</span>
                        {user.permissions.length} permissions
                      </button>
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
                      <button
                        type="button"
                        onClick={() => {
                          setResetUser(user);
                          setResetPassword("");
                        }}
                        className="inline-flex items-center gap-1.5 rounded bg-surface-container-low px-3 py-2 text-xs font-bold text-on-surface hover:bg-surface-container-high"
                      >
                        <span className="material-symbols-outlined text-[16px]">lock_reset</span>
                        Reset password
                      </button>
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
              <div>
                <h2 className="text-2xl font-black tracking-tight text-on-surface">{t.admin.permissionsTitle}</h2>
                {permissionUser && <p className="mt-1 text-sm text-on-surface-variant">{permissionUser.username}</p>}
              </div>
              <button type="button" onClick={() => { setIsPermissionsOpen(false); setPermissionUser(null); }} className="material-symbols-outlined p-1 text-[28px] text-on-surface-variant hover:text-on-surface">close</button>
            </div>
            <div className="px-8 py-7">
              <div className="max-h-[55vh] space-y-5 overflow-y-auto pr-2">
                {permissionUser ? (
                  permissionUser.permissions.length > 0 ? permissionUser.permissions.map((permission) => (
                    <PermissionRow key={permission} permission={permission} />
                  )) : <p className="text-sm text-on-surface-variant">No effective permissions.</p>
                ) : (
                  (rolesList ?? []).map((role) => (
                    <div key={role.id} className="border-b border-outline-variant/10 pb-5 last:border-0">
                      <div className="mb-3 flex items-center gap-3">
                        <span className={`h-2.5 w-2.5 rounded-full ${roleDots[role.role_name.toLowerCase()] ?? "bg-outline-variant"}`} />
                        <p className="text-base font-black uppercase tracking-wide text-on-surface">{role.role_name}</p>
                      </div>
                      <div className="space-y-2 pl-5">
                        {role.permissions.map((permission) => <PermissionRow key={permission} permission={permission} />)}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
            <div className="flex justify-end bg-surface-container-low px-8 py-5">
              <button type="button" onClick={() => { setIsPermissionsOpen(false); setPermissionUser(null); }} className="bg-surface-container px-6 py-3 text-sm font-bold text-on-surface hover:bg-surface-container-high">{t.common.close}</button>
>>>>>>> Stashed changes
            </div>
          </div>
          <button
            type="submit"
            disabled={createUser.isPending || isLoadingRoles}
            className="inline-flex items-center justify-center gap-2 self-end rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
          >
<<<<<<< Updated upstream
            <UserPlus size={16} />
            Tao user
          </button>
        </form>

        <section className="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <div className="grid grid-cols-[1.2fr_2fr_auto] border-b border-slate-100 px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
            <span>User</span>
            <span>Role</span>
            <span>Hanh dong</span>
          </div>

          {isLoadingUsers ? (
            <div className="p-5 text-sm text-slate-500">Dang tai user...</div>
          ) : users.length === 0 ? (
            <div className="p-5 text-sm text-slate-500">Chua co user.</div>
          ) : (
            users.map((user) => {
              const selectedRoles =
                roleDrafts[user.id] ?? userRoleDefaults[user.id] ?? []
              return (
                <div
                  key={user.id}
                  className="grid grid-cols-[1.2fr_2fr_auto] items-center gap-4 border-b border-slate-100 px-5 py-4 last:border-b-0"
                >
                  <div>
                    <p className="font-semibold text-slate-900">{user.username}</p>
                    <p className="mt-1 break-all font-mono text-xs text-slate-400">
                      {user.id}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {assignableRoles.map((role) => (
                      <label
                        key={role.id}
                        className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-700"
                      >
                        <input
                          type="checkbox"
                          checked={selectedRoles.includes(role.role_name)}
                          onChange={() =>
                            toggleRole(role.role_name, selectedRoles, (next) =>
                              setRoleDrafts((current) => ({
                                ...current,
                                [user.id]: next,
                              })),
                            )
                          }
                        />
                        {role.role_name}
                      </label>
                    ))}
                  </div>
                  <button
                    type="button"
                    onClick={() =>
                      assignRoles.mutate({
                        userId: user.id,
                        roles: selectedRoles.length ? selectedRoles : ["viewer"],
                      })
                    }
                    disabled={assignRoles.isPending}
                    className="inline-flex items-center gap-2 rounded-lg border border-blue-200 px-3 py-2 text-sm font-medium text-blue-700 hover:bg-blue-50 disabled:opacity-50"
                  >
                    <ShieldCheck size={16} />
                    Luu role
                  </button>
                </div>
              )
            })
          )}
        </section>
      </div>
    </main>
  )
=======
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
                  type="password" required minLength={8} maxLength={128} value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full bg-surface-container-lowest border-none ring-1 ring-inset ring-outline-variant/40 focus:ring-2 focus:ring-inset focus:ring-tertiary rounded-lg px-3 py-2.5 text-sm"
                />
              </div>
              <PasswordPolicy value={newPassword} />
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

      {resetUser && (
        <div className="fixed inset-0 z-[95] flex items-center justify-center bg-black/35 p-4 backdrop-blur-sm" role="dialog" aria-modal="true">
          <form onSubmit={(e) => { e.preventDefault(); void handleResetPassword(); }} className="w-full max-w-md overflow-hidden bg-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-outline-variant/10 px-8 py-6">
              <div>
                <h2 className="text-2xl font-black text-on-surface">Reset password</h2>
                <p className="mt-1 text-sm text-on-surface-variant">{resetUser.username}</p>
              </div>
              <button type="button" onClick={() => setResetUser(null)} className="material-symbols-outlined text-[28px] text-on-surface-variant">close</button>
            </div>
            <div className="space-y-4 px-8 py-7">
              <label className="block text-sm font-medium text-on-surface" htmlFor="reset-password">New password</label>
              <input id="reset-password" type="password" required minLength={8} maxLength={128} autoComplete="new-password" value={resetPassword} onChange={(e) => setResetPassword(e.target.value)} className="w-full rounded-lg border-none bg-surface-container-lowest px-3 py-2.5 text-sm ring-1 ring-inset ring-outline-variant/40 focus:ring-2 focus:ring-tertiary" />
              <PasswordPolicy value={resetPassword} />
            </div>
            <div className="flex justify-end gap-3 bg-surface-container-low px-8 py-5">
              <button type="button" onClick={() => setResetUser(null)} className="bg-surface-container px-6 py-3 text-sm font-bold">{t.common.cancel}</button>
              <button type="submit" disabled={resetPasswordMutation.isPending} className="bg-tertiary px-6 py-3 text-sm font-bold text-on-tertiary disabled:opacity-60">
                {resetPasswordMutation.isPending ? t.common.loading : "Reset password"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
>>>>>>> Stashed changes
}

function PermissionRow({ permission }: { permission: string }) {
  const separator = permission.indexOf(":");
  const method = separator >= 0 ? permission.slice(0, separator) : "API";
  const path = separator >= 0 ? permission.slice(separator + 1) : permission;
  const action: Record<string, string> = { GET: "View", POST: "Create / perform", PUT: "Update", PATCH: "Update", DELETE: "Delete" };
  return (
    <div className="flex items-start gap-2 text-sm">
      <span className="min-w-16 rounded bg-surface-container-low px-2 py-0.5 text-center text-[11px] font-black text-tertiary">{method}</span>
      <div className="min-w-0">
        <p className="font-medium text-on-surface">{action[method] ?? "Access"}</p>
        <p className="break-all text-xs text-on-surface-variant">{path}</p>
      </div>
    </div>
  );
}

function PasswordPolicy({ value }: { value: string }) {
  return (
    <ul className="grid gap-1 text-xs text-on-surface-variant sm:grid-cols-2">
      {getPasswordPolicyChecks(value).map((check) => (
        <li key={check.label} className={`flex items-center gap-1 ${check.valid ? "text-emerald-700" : ""}`}>
          <span className="material-symbols-outlined text-[14px]">{check.valid ? "check_circle" : "radio_button_unchecked"}</span>
          {check.label}
        </li>
      ))}
    </ul>
  );
}
