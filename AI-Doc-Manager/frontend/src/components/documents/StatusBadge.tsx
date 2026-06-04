import { DocumentStatus } from "@/types/document"

const CONFIG: Record<DocumentStatus, { label: string; className: string }> = {
  [DocumentStatus.DRAFT]: {
    label: "Draft",
    className: "bg-slate-100 text-slate-600",
  },
  [DocumentStatus.PENDING_REVIEW]: {
    label: "Pending Review",
    className: "bg-amber-100 text-amber-700",
  },
  [DocumentStatus.APPROVED]: {
    label: "Approved",
    className: "bg-emerald-100 text-emerald-700",
  },
  [DocumentStatus.REJECTED]: {
    label: "Rejected",
    className: "bg-red-100 text-red-600",
  },
  [DocumentStatus.EXPIRED]: {
    label: "Expired",
    className: "bg-slate-100 text-slate-400 line-through",
  },
  [DocumentStatus.ARCHIVED]: {
    label: "Archived",
    className: "bg-slate-100 text-slate-500",
  },
}

export function StatusBadge({ status }: { status: DocumentStatus }) {
  const { label, className } = CONFIG[status] ?? CONFIG[DocumentStatus.DRAFT]

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${className}`}
    >
      {label}
    </span>
  )
}
