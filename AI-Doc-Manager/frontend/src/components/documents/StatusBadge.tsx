import { DocumentStatus } from "@/types/document"

const CONFIG: Record<string, { label: string; className: string }> = {
  [DocumentStatus.DRAFT]:          { label: "Nháp",         className: "bg-slate-100 text-slate-600" },
  [DocumentStatus.PENDING_REVIEW]: { label: "Chờ duyệt",    className: "bg-amber-100 text-amber-700" },
  [DocumentStatus.APPROVED]:       { label: "Đã duyệt",     className: "bg-emerald-100 text-emerald-700" },
  [DocumentStatus.REJECTED]:       { label: "Từ chối",      className: "bg-red-100 text-red-600" },
  [DocumentStatus.EXPIRED]:        { label: "Hết hạn",      className: "bg-slate-100 text-slate-400 line-through" },
  draft:                           { label: "Nháp",         className: "bg-slate-100 text-slate-600" },
  pending_review:                  { label: "Chờ duyệt",    className: "bg-amber-100 text-amber-700" },
  approved:                        { label: "Đã duyệt",     className: "bg-emerald-100 text-emerald-700" },
  rejected:                        { label: "Từ chối",      className: "bg-red-100 text-red-600" },
  expired:                         { label: "Hết hạn",      className: "bg-slate-100 text-slate-400 line-through" },
  archived:                        { label: "Lưu trữ",      className: "bg-slate-100 text-slate-500" },
}

export function StatusBadge({ status }: { status: DocumentStatus | string }) {
  const normalizedStatus = String(status).toLowerCase()
  const { label, className } =
    CONFIG[status] ?? CONFIG[normalizedStatus] ?? CONFIG[DocumentStatus.DRAFT]

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${className}`}
    >
      {label}
    </span>
  )
}
