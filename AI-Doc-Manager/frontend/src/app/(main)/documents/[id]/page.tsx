"use client"

<<<<<<< Updated upstream
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
=======
import { use, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import DocumentPreview from "@/components/documents/DocumentPreview";
import { DocumentReviewPanel } from "@/components/documents/DocumentReviewPanel";
import DocumentSidebar, {
  DocumentDetailData,
} from "@/components/documents/DocumentSidebar";
import { useDocument, useApproveDocument, useRejectDocument, useCreateReview } from "@/hooks/useDocuments";
import { usePermission } from "@/hooks/usePermission";
import { useTranslation } from "@/i18n/LanguageContext";
import { toast } from "sonner";
import apiClient from "@/lib/api/client";
import { ragApi } from "@/lib/api/rag";
import { validateRejectReason, validateReviewComment, validateReviewGrade } from "@/lib/validation";

function mapDocumentToSidebar(doc: any, t: any): DocumentDetailData {
  const statusLabels: Record<string, string> = {
    draft: t.status.draft,
    pending_review: t.status.pending_review,
    approved: t.status.approved,
    rejected: t.status.rejected,
    expired: t.status.expired,
    archived: t.status.archived,
  };

  return {
    id: doc.document_id ?? doc.id,
    title: doc.title ?? doc.original_filename ?? "Untitled",
    filename: doc.original_filename ?? "—",
    creatorName: doc.created_by_name ?? "Unknown user",
    status: statusLabels[doc.status] ?? doc.status ?? "Draft",
    version: `v${doc.version ?? 1}.0`,
    averageReviewGrade: doc.average_review_grade,
    reviewCount: doc.review_count ?? 0,
    aiAssessment: {
      score: doc.rag_ingestion_status === "completed" ? "✓" : "—",
      label: doc.rag_ingestion_status === "completed"
        ? t.documents.detail.vectorized
        : t.documents.detail.notVectorized,
      summary: doc.rag_ingestion_status === "completed"
        ? t.documents.detail.vectorized
        : (doc.rag_ingestion_error ?? t.documents.detail.notVectorized),
      points: doc.rag_ingestion_status === "completed"
        ? [{ isPositive: true, text: t.documents.detail.vectorized }]
        : [],
    },
    reviewer: (doc.approved_by_name || doc.rejected_by_name)
      ? {
          name: doc.approved_by_name ?? doc.rejected_by_name ?? "Reviewer",
          role: "Reviewer",
          avatar: "",
          comment: doc.rejected_reason ?? "Workflow decision recorded.",
          statusLabel:
            doc.status === "approved"
              ? t.status.approved
              : doc.status === "rejected"
                ? t.status.rejected
                : t.approvals.submitted,
        }
      : null,
  };
}

export default function DocumentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const documentId = resolvedParams.id;
  const { t } = useTranslation();
  const perm = usePermission();
  const searchParams = useSearchParams();

  const { data: document, isLoading, error, refetch: refetchDoc } = useDocument(documentId);
  const { data: ragStatus, refetch: refetchRagStatus } = useQuery({
    queryKey: ["rag", "status", documentId],
    queryFn: () => ragApi.status(documentId),
    refetchInterval: (query) => {
      const data = query.state.data;
      return data && ["pending", "ingesting"].includes(data.status) ? 5000 : false;
    },
    enabled: !!document && perm.canViewRag,
  });

  const refetch = () => {
    refetchDoc();
    refetchRagStatus();
  };

  const approveMutation = useApproveDocument();
  const rejectMutation = useRejectDocument();
  const reviewMutation = useCreateReview(documentId);

  const [activeTab, setActiveTab] = useState<"preview" | "reviews">(
    searchParams.get("tab") === "reviews" ? "reviews" : "preview",
  );

  // New version upload state
  const [isUploadingVersion, setIsUploadingVersion] = useState(false);
  const [isExpiring, setIsExpiring] = useState(false);
  const [isRevectorizing, setIsRevectorizing] = useState(false);
  const [isDeletingVectors, setIsDeletingVectors] = useState(false);

  const deriveRole = (): "viewer" | "editor" | "approver" => {
    if (perm.canApprove) return "approver";
    if (perm.canUpload) return "editor";
    return "viewer";
  };

  const handleApprove = async (grade: number, comment: string) => {
    const validationError = validateReviewGrade(grade) ?? validateReviewComment(comment);
    if (validationError) return toast.error(validationError);
    try {
      await reviewMutation.mutateAsync({ grade, comment: comment.trim() });
      await approveMutation.mutateAsync(documentId);
      toast.success(t.status.approved);
      refetch();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? t.errors.approveFailed);
    }
  };

  const handleReject = async (grade: number, comment: string) => {
    const validationError = validateReviewGrade(grade) ?? validateReviewComment(comment) ?? validateRejectReason(comment);
    if (validationError) return toast.error(validationError);
    try {
      await reviewMutation.mutateAsync({ grade, comment: comment.trim() });
      await rejectMutation.mutateAsync({ id: documentId, reason: comment.trim() });
      toast.success(t.status.rejected);
      refetch();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? t.errors.rejectFailed);
    }
  };

  const handleNewVersion = async (file: File) => {
    setIsUploadingVersion(true);
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
  }
=======
  };

  const handleRevectorize = async () => {
    setIsRevectorizing(true);
    try {
      await ragApi.ingest(documentId, true);
      toast.success(t.documents.detail.revectorize);
      refetch();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? t.errors.generic);
    } finally {
      setIsRevectorizing(false);
    }
  };

  const handleDeleteVectors = async () => {
    if (!confirm("Are you sure you want to delete the vectors for this document?")) return;
    setIsDeletingVectors(true);
    try {
      await ragApi.remove(documentId);
      toast.success(t.documents.detail.deleteVectorsSuccess ?? "Vectors deleted successfully");
      refetch();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? t.errors.generic);
    } finally {
      setIsDeletingVectors(false);
    }
  };

  // File input ref for new version
  const triggerNewVersionUpload = () => {
    const input = window.document.createElement("input");
    input.type = "file";
    input.accept = ".pdf,.doc,.docx";
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) handleNewVersion(file);
    };
    input.click();
  };
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
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
=======
  const effectiveRagStatus = ragStatus?.status ?? document.rag_ingestion_status;
  const sidebarData = mapDocumentToSidebar(
    { ...document, rag_ingestion_status: effectiveRagStatus },
    t,
  );
  const userRole = deriveRole();
  const isPending = document.status === "pending_review";
  const isApproved = document.status === "approved";

  return (
    <div className="p-8 flex gap-8 h-[calc(100vh-4rem)] overflow-hidden">
      {/* Left: document preview and reader reviews */}
      <div className="flex min-w-0 flex-1 flex-col gap-3">
        <nav className="flex shrink-0 items-center gap-1 rounded-xl border border-outline-variant/15 bg-white p-1 shadow-sm" aria-label="Document detail sections">
          <button type="button" onClick={() => setActiveTab("preview")} className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-bold ${activeTab === "preview" ? "bg-tertiary text-on-tertiary" : "text-on-surface-variant hover:bg-surface-container-low"}`}>
            <span className="material-symbols-outlined text-[18px]">preview</span>
            Preview
          </button>
          {perm.canViewReviews && (
            <button type="button" onClick={() => setActiveTab("reviews")} className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-bold ${activeTab === "reviews" ? "bg-tertiary text-on-tertiary" : "text-on-surface-variant hover:bg-surface-container-low"}`}>
              <span className="material-symbols-outlined text-[18px]">reviews</span>
              {t.documents.detail.reviews}
              <span className="rounded-full bg-black/10 px-2 py-0.5 text-[11px]">{document.review_count}</span>
            </button>
          )}
        </nav>
        {activeTab === "preview" ? (
          <DocumentPreview
        title={document.title ?? document.original_filename ?? "Untitled"}
        description={document.description ?? t.documents.detail.noDescription}
        previewUrl={document.preview_url}
        downloadUrl={document.download_url}
        filename={document.original_filename}
        contentType={document.content_type}
        content={
          <div className="space-y-4">
            <div className="flex flex-wrap gap-3 text-sm text-on-surface-variant">
              <span className="bg-surface-container-low px-3 py-1 rounded-full">
                {t.documents.detail.typeLabel}: {document.document_type ?? "N/A"}
              </span>
              <span className="bg-surface-container-low px-3 py-1 rounded-full">
                {t.documents.detail.fileLabel}: {document.original_filename ?? "N/A"}
              </span>
              <span className="bg-surface-container-low px-3 py-1 rounded-full">
                {t.documents.detail.sizeLabel}:{" "}
                {document.file_size != null
                  ? `${(document.file_size / 1024).toFixed(1)} KB`
                  : "N/A"}
              </span>
              <span
                className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  effectiveRagStatus === "completed"
                    ? "bg-green-100 text-green-800"
                    : "bg-yellow-100 text-yellow-800"
                }`}
              >
                {effectiveRagStatus === "completed"
                  ? t.documents.detail.vectorized
                  : t.documents.detail.notVectorized}
              </span>
            </div>
            {document.download_url && (
              <div>
                <a
                  href={document.download_url}
                  download={document.original_filename}
                  className="inline-flex items-center gap-2 text-tertiary font-semibold text-sm hover:underline"
                >
                  <span className="material-symbols-outlined text-[18px]">download</span>
                  {t.documents.detail.downloadOriginal}
                </a>
              </div>
            )}
            {effectiveRagStatus !== "completed" && isPending && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-800">
                {t.documents.detail.notVectorizedNotice}
              </div>
            )}

            {/* Additional actions */}
            <div className="border-t border-surface-variant/30 pt-4 mt-4">
              <div className="flex flex-wrap gap-2">
                {(perm.canUpload || perm.canExpire) && (
                  <>
                    {perm.canUpload && <button
                      onClick={triggerNewVersionUpload}
                      disabled={isUploadingVersion}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-outline-variant/40 text-on-surface-variant hover:bg-surface-container-low transition-colors disabled:opacity-50"
                    >
                      <span className="material-symbols-outlined text-[16px]">upload</span>
                      {isUploadingVersion ? t.common.loading : t.documents.detail.newVersion}
                    </button>}
                    {perm.canExpire && <button
                      onClick={handleExpire}
                      disabled={isExpiring}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-outline-variant/40 text-on-surface-variant hover:bg-surface-container-low transition-colors disabled:opacity-50"
                    >
                      <span className="material-symbols-outlined text-[16px]">timer_off</span>
                      {isExpiring ? t.common.loading : t.documents.detail.expire}
                    </button>}
                  </>
                )}
                {isApproved && perm.canManageRag && (
                  <button
                    onClick={handleRevectorize}
                    disabled={isRevectorizing}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-outline-variant/40 text-on-surface-variant hover:bg-surface-container-low transition-colors disabled:opacity-50"
                  >
                    <span className="material-symbols-outlined text-[16px]">auto_awesome</span>
                    {isRevectorizing ? t.common.loading : t.documents.detail.revectorize}
                  </button>
                )}
                {isApproved && perm.canManageRag && effectiveRagStatus === "completed" && (
                  <button
                    onClick={handleDeleteVectors}
                    disabled={isDeletingVectors}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-red-200 text-red-700 hover:bg-red-50 transition-colors disabled:opacity-50"
                  >
                    <span className="material-symbols-outlined text-[16px]">delete</span>
                    {isDeletingVectors ? t.common.loading : t.documents.detail.deleteVectors}
                  </button>
                )}
>>>>>>> Stashed changes
              </div>
              <StatusBadge status={doc.status} />
            </div>
            <p className="text-sm text-slate-500">
              {TYPE_LABEL[doc.document_type]} · v{doc.version} ·{" "}
              {doc.size_bytes ? formatFileSize(doc.size_bytes) : "--"} ·{" "}
              tạo lúc {formatDate(doc.created_at)}
            </p>
          </div>
<<<<<<< Updated upstream

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
=======
        }
          />
        ) : (
          <DocumentReviewPanel
            documentId={documentId}
            averageGrade={document.average_review_grade}
            reviewCount={document.review_count}
            canComment={perm.canComment}
            status={document.status}
          />
        )}
      </div>

      {/* Right: Sidebar with approval workflow */}
      <DocumentSidebar
        data={sidebarData}
        userRole={userRole}
        onApprove={handleApprove}
        onReject={handleReject}
        isApproving={approveMutation.isPending || reviewMutation.isPending}
        isRejecting={rejectMutation.isPending || reviewMutation.isPending}
      />
>>>>>>> Stashed changes
    </div>
  )
}
