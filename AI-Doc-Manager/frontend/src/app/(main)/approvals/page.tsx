"use client"

import { useQuery } from "@tanstack/react-query"
import { approvalsApi } from "@/lib/api/approvals"
import { StatusBadge } from "@/components/documents/StatusBadge"
import { ApprovalActions } from "@/components/approvals/ApprovalActions"
import Link from "next/link"

export default function ApprovalsPage() {
  const { data: queue, isLoading, refetch } = useQuery({
    queryKey: ["approvals", "queue"],
    queryFn:  approvalsApi.getPendingQueue,
  })

  return (
    <div className="space-y-6 min-w-0">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Phê duyệt</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          {queue?.length ?? "…"} tài liệu đang chờ xét duyệt
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden min-w-0">
        {isLoading ? (
          <div className="p-6 space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-14 bg-slate-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : !queue?.length ? (
          <div className="py-16 text-center text-slate-400 text-sm">
            Không có tài liệu nào đang chờ duyệt 🎉
          </div>
        ) : (
          <ul className="divide-y divide-slate-100">
            {queue.map((doc) => (
              <li key={doc.id} className="flex items-center justify-between px-5 py-4 gap-4 hover:bg-slate-50 transition-colors min-w-0">
                <div className="min-w-0 flex-1">
                  <Link
                    href={`/documents/${doc.id}`}
                    className="font-medium text-slate-800 hover:text-blue-600 text-sm truncate block"
                  >
                    {doc.file_link.split("/").pop()}
                  </Link>
                  <p className="text-xs text-slate-400 mt-0.5">
                    v{doc.version} · {doc.created_by_name} ·{" "}
                    {new Date(doc.created_at).toLocaleDateString("vi-VN")}
                  </p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <StatusBadge status={doc.status} />
                  <ApprovalActions documentId={doc.id} onDone={() => refetch()} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
