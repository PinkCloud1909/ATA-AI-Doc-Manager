"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import { Download, FileText, History } from "lucide-react"
import { toast } from "sonner"
import { documentsApi } from "@/lib/api/documents"
import { formatFileSize } from "@/lib/gcs"
import { useDocument } from "@/hooks/useDocuments"
import { usePermission } from "@/hooks/usePermission"
import { StatusBadge } from "@/components/documents/StatusBadge"
import { VersionHistory } from "@/components/documents/VersionHistory"
import { ReviewForm } from "@/components/documents/ReviewForm"
import { ApprovalActions } from "@/components/approvals/ApprovalActions"
import { DocumentStatus, DocumentType } from "@/types/document"

const TYPE_LABEL: Record<DocumentType, string> = {
  [DocumentType.POLICY]: "Policy",
  [DocumentType.MANUAL]: "Manual / Runbook",
  [DocumentType.REPORT]: "Report",
  [DocumentType.OTHER]: "Other",
}

function formatDate(value?: string | null) {
  if (!value) return "--"
  return new Date(value).toLocaleString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export default function DocumentDetailPage() {
  const params = useParams<{ id: string }>()
  const documentId = params.id
  const { data: doc, isLoading, error, refetch } = useDocument(documentId)
  const perm = usePermission()
  const [isExpiring, setIsExpiring] = useState(false)

  const handleDownload = async () => {
    if (!doc) return
    try {
      const blob = await documentsApi.downloadFile(doc.id)
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement("a")
      anchor.href = url
      anchor.download = doc.original_filename || `${doc.title}.bin`
      anchor.click()
      URL.revokeObjectURL(url)
    } catch {
      toast.error("Không tải được file")
    }
  }

  const handleExpire = async () => {
    if (!doc) return
    setIsExpiring(true)
    try {
      await documentsApi.expire(doc.id)
      toast.success("Đã đánh dấu tài liệu là Expired")
      await refetch()
    } catch {
      toast.error("Không thể đánh dấu Expired")
    } finally {
      setIsExpiring(false)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-4 p-8">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="h-20 animate-pulse rounded-xl bg-slate-100" />
        ))}
      </div>
    )
  }

  if (error || !doc) {
    return (
      <div className="p-8">
        <div className="rounded-lg border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
          Không tải được tài liệu. Vui lòng đăng nhập lại hoặc kiểm tra quyền truy cập.
        </div>
      </div>
    )
  }

  const canSubmit = perm.canUpload && doc.status === DocumentStatus.DRAFT
  const canApprove = perm.canApprove && doc.status === DocumentStatus.PENDING_REVIEW
  const canReview =
    perm.canReview &&
    doc.status === DocumentStatus.PENDING_REVIEW ||
    (perm.canReview && doc.status === DocumentStatus.APPROVED)
  const canExpire =
    perm.canExpire &&
    [
      DocumentStatus.PENDING_REVIEW,
      DocumentStatus.APPROVED,
      DocumentStatus.REJECTED,
    ].includes(doc.status)

  return (
    <div className="h-full overflow-y-auto p-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                <FileText size={20} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">{doc.title}</h1>
                <p className="text-sm text-slate-500">{doc.original_filename}</p>
              </div>
              <StatusBadge status={doc.status} />
            </div>
            <p className="text-sm text-slate-500">
              {TYPE_LABEL[doc.document_type]} · v{doc.version} ·{" "}
              {doc.size_bytes ? formatFileSize(doc.size_bytes) : "--"} ·{" "}
              tạo lúc {formatDate(doc.created_at)}
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={handleDownload}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              <Download size={16} />
              Tải xuống
            </button>
            {(canSubmit || canApprove) && (
              <ApprovalActions
                documentId={doc.id}
                showSubmit={canSubmit}
                showApprove={canApprove}
                onDone={() => refetch()}
              />
            )}
            {canExpire && (
              <button
                type="button"
                onClick={handleExpire}
                disabled={isExpiring}
                className="inline-flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-1.5 text-sm font-medium text-amber-700 hover:bg-amber-100 disabled:opacity-50"
              >
                <History size={16} />
                Mark Expired
              </button>
            )}
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
          <div className="space-y-6">
            <section className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="mb-3 text-sm font-semibold text-slate-700">Thông tin</h2>
              <dl className="grid gap-3 text-sm md:grid-cols-2">
                <div>
                  <dt className="text-xs text-slate-400">Document ID</dt>
                  <dd className="mt-0.5 break-all font-mono text-slate-700">{doc.id}</dd>
                </div>
                <div>
                  <dt className="text-xs text-slate-400">Group ID</dt>
                  <dd className="mt-0.5 break-all font-mono text-slate-700">
                    {doc.document_group_id}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs text-slate-400">Content type</dt>
                  <dd className="mt-0.5 text-slate-700">{doc.content_type || "--"}</dd>
                </div>
                <div>
                  <dt className="text-xs text-slate-400">Điểm trung bình</dt>
                  <dd className="mt-0.5 font-semibold text-slate-700">
                    {doc.avg_grade != null ? `${doc.avg_grade.toFixed(1)} / 10` : "--"}
                  </dd>
                </div>
              </dl>
              {doc.description && (
                <p className="mt-4 border-t border-slate-100 pt-4 text-sm text-slate-600">
                  {doc.description}
                </p>
              )}
              <p className="mt-4 break-all border-t border-slate-100 pt-4 font-mono text-xs text-slate-400">
                {doc.file_link}
              </p>
            </section>

            <section className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="mb-3 text-sm font-semibold text-slate-700">
                Đánh giá ({doc.reviews?.length ?? 0})
              </h2>
              {!doc.reviews?.length ? (
                <p className="text-sm text-slate-400">Chưa có đánh giá.</p>
              ) : (
                <div className="space-y-3">
                  {doc.reviews.map((review) => (
                    <div key={review.id} className="rounded-lg bg-slate-50 p-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-slate-700">
                          {review.reviewer_name ?? "Reviewer"}
                        </span>
                        <span className="text-sm font-bold text-blue-600">
                          {review.grade}/10
                        </span>
                      </div>
                      <p className="mt-1 text-sm text-slate-600">{review.comment}</p>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {canReview && <ReviewForm documentId={doc.id} />}
          </div>

          <aside className="space-y-4">
            <section className="rounded-xl border border-slate-200 bg-white p-5">
              <VersionHistory groupId={doc.id} currentDocumentId={doc.id} />
            </section>
          </aside>
        </div>
      </div>
    </div>
  )
}
