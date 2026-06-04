"use client"

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
    onChange([...selectedRoles, value])
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
            </div>
          </div>
          <button
            type="submit"
            disabled={createUser.isPending || isLoadingRoles}
            className="inline-flex items-center justify-center gap-2 self-end rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
          >
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
}
