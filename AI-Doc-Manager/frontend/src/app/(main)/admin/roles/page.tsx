"use client"

import { useQuery } from "@tanstack/react-query"
import { Shield } from "lucide-react"
import { adminApi } from "@/lib/api/admin"

const ROLE_LABELS: Record<string, string> = {
  admin: "Toàn quyền hệ thống",
  viewer: "Xem tài liệu Approved / Expired",
  editor: "Tạo, sửa version, gửi phê duyệt",
  reviewer: "Chấm điểm, phê duyệt, từ chối, đánh dấu Expired",
  user: "Alias viewer cho user đăng ký cũ",
}

export default function AdminRolesPage() {
  const { data: roles = [], isLoading, error } = useQuery({
    queryKey: ["admin", "roles"],
    queryFn: adminApi.listRoles,
  })

  return (
    <main className="h-full overflow-y-auto p-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Role & quyền</h1>
          <p className="mt-1 text-sm text-slate-500">
            Danh sách role và endpoint privilege đang được backend enforce.
          </p>
        </div>

        {error && (
          <div className="rounded-lg border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
            Không tải được danh sách role. Kiểm tra backend và quyền admin.
          </div>
        )}

        {isLoading ? (
          <div className="rounded-lg border border-slate-200 bg-white p-5 text-sm text-slate-500">
            Đang tải role...
          </div>
        ) : (
          <div className="grid gap-4 lg:grid-cols-2">
            {roles.map((role) => (
              <section
                key={role.id}
                className="rounded-lg border border-slate-200 bg-white p-5"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                      <Shield size={18} />
                    </div>
                    <div>
                      <h2 className="text-lg font-semibold text-slate-900">
                        {role.role_name}
                      </h2>
                      <p className="text-sm text-slate-500">
                        {ROLE_LABELS[role.role_name] ?? role.description ?? "Custom role"}
                      </p>
                    </div>
                  </div>
                  <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">
                    {role.privileges?.length ?? 0} quyền
                  </span>
                </div>

                <div className="mt-4 max-h-80 overflow-y-auto rounded-lg bg-slate-50 p-3">
                  {!role.privileges?.length ? (
                    <p className="text-sm text-slate-400">Chưa có privilege.</p>
                  ) : (
                    <ul className="space-y-2">
                      {role.privileges.map((privilege) => (
                        <li
                          key={privilege.id}
                          className="break-all rounded-md bg-white px-3 py-2 font-mono text-xs text-slate-600"
                        >
                          {privilege.api_endpoint}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </section>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
