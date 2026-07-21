"use client"

<<<<<<< Updated upstream
import Link from "next/link"
import { useQuery } from "@tanstack/react-query"
import { approvalsApi } from "@/lib/api/approvals"
import { StatusBadge } from "@/components/documents/StatusBadge"
import { ApprovalActions } from "@/components/approvals/ApprovalActions"

export default function ApprovalsPage() {
  const {
    data: queue,
    isLoading,
    refetch,
    error,
  } = useQuery({
    queryKey: ["approvals", "queue"],
    queryFn: approvalsApi.getPendingQueue,
  })
=======
import { useTranslation, formatT } from "@/i18n/LanguageContext";
import { usePendingApprovals } from "@/hooks/useDocuments";
import { StatusBadge } from "@/components/documents/StatusBadge";
import { ApprovalActions } from "@/components/approvals/ApprovalActions";
import Link from "next/link";

export default function ApprovalsPage() {
  const { t } = useTranslation();
  const { data: queue, isLoading } = usePendingApprovals();
>>>>>>> Stashed changes

  return (
    <div className="min-w-0 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Phê duyệt</h1>
        <p className="mt-0.5 text-sm text-slate-500">
          {queue?.length ?? 0} tài liệu đang chờ xét duyệt
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
          Không tải được hàng đợi phê duyệt. Vui lòng đăng nhập lại hoặc kiểm tra quyền truy cập.
        </div>
      )}

      <div className="min-w-0 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        {isLoading ? (
          <div className="space-y-3 p-6">
            {Array.from({ length: 3 }).map((_, index) => (
              <div key={index} className="h-14 animate-pulse rounded-lg bg-slate-100" />
            ))}
          </div>
        ) : !queue?.length ? (
          <div className="py-16 text-center text-sm text-slate-400">
            Không có tài liệu nào đang chờ duyệt.
          </div>
        ) : (
          <ul className="divide-y divide-slate-100">
            {queue.map((doc) => (
              <li
                key={doc.id}
                className="flex min-w-0 items-center justify-between gap-4 px-5 py-4 transition-colors hover:bg-slate-50"
              >
                <div className="min-w-0 flex-1">
                  <Link
                    href={`/documents/${doc.id}`}
                    className="block truncate text-sm font-medium text-slate-800 hover:text-blue-600"
                  >
<<<<<<< Updated upstream
                    {doc.title || doc.original_filename}
                  </Link>
                  <p className="mt-0.5 text-xs text-slate-400">
                    v{doc.version} · {doc.created_by_name || "admin"} ·{" "}
                    {new Date(doc.created_at).toLocaleDateString("vi-VN")}
=======
                    {doc.title}
                  </Link>
                  <p className="text-xs text-slate-400 mt-0.5">
                    v{doc.version} · {doc.submitted_by_name ?? doc.created_by_name ?? "Unknown user"} ·{" "}
                    {doc.submitted_at
                      ? new Date(doc.submitted_at).toLocaleDateString("vi-VN")
                      : ""}
>>>>>>> Stashed changes
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-3">
                  <StatusBadge status={doc.status} />
                  <ApprovalActions
<<<<<<< Updated upstream
                    documentId={doc.id}
                    showSubmit={false}
                    showApprove
                    onDone={() => refetch()}
=======
                    documentId={doc.document_id}
>>>>>>> Stashed changes
                  />
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
