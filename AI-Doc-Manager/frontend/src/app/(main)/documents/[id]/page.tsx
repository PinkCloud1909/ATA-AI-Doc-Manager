"use client";

import { use, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import DocumentPreview from "@/components/documents/DocumentPreview";
import DocumentSidebar, {
  DocumentDetailData,
} from "@/components/documents/DocumentSidebar";
import { useDocument, useApproveDocument, useRejectDocument, useCreateReview } from "@/hooks/useDocuments";
import { usePermission } from "@/hooks/usePermission";
import { useTranslation } from "@/i18n/LanguageContext";
import { toast } from "sonner";
import apiClient from "@/lib/api/client";
import { vectorizationApi } from "@/lib/api/vectorization";

function mapDocumentToSidebar(doc: any, t: any): DocumentDetailData {
  const statusLabels: Record<string, string> = {
    draft: t.status.draft,
    pending_review: t.status.pending_review,
    approved: t.status.approved,
    rejected: t.status.rejected,
    expired: t.status.expired,
    archived: t.status.archived,
  };

  const reviews = doc.reviews ?? [];
  const latestReview = reviews.length > 0 ? reviews[reviews.length - 1] : null;

  return {
    id: doc.document_id ?? doc.id,
    title: doc.title ?? doc.original_filename ?? "Untitled",
    status: statusLabels[doc.status] ?? doc.status ?? "Draft",
    version: `v${doc.version ?? 1}.0`,
    aiAssessment: {
      score: doc.is_vectorized ? "--" : "--",
      label: doc.is_vectorized
        ? t.documents.detail.vectorized
        : t.documents.detail.notVectorized,
      summary: doc.is_vectorized
        ? t.documents.detail.vectorized
        : t.documents.detail.notVectorized,
      points: doc.is_vectorized
        ? [{ isPositive: true, text: t.documents.detail.vectorized }]
        : [],
    },
    reviewer: latestReview
      ? {
          name: latestReview.reviewer_name ?? "Reviewer",
          role: "Reviewer",
          avatar: "",
          comment: latestReview.comment ?? "",
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

  const { data: document, isLoading, error, refetch: refetchDoc } = useDocument(documentId);
  const { data: vecStatus, refetch: refetchVecStatus } = useQuery({
    queryKey: ["vectorization", "status", documentId],
    queryFn: () => vectorizationApi.getStatus(documentId),
    refetchInterval: (query) => {
      const data = query.state.data;
      return data && !data.is_vectorized ? 5000 : false;
    },
    enabled: !!document,
  });

  const refetch = () => {
    refetchDoc();
    refetchVecStatus();
  };

  const perm = usePermission();
  const approveMutation = useApproveDocument();
  const rejectMutation = useRejectDocument();
  const reviewMutation = useCreateReview(documentId);

  const [pendingAction, setPendingAction] = useState<{
    type: "approve" | "reject";
    grade: number;
    comment: string;
  } | null>(null);

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

  const handleApprove = (grade: number, comment: string) => {
    setPendingAction({ type: "approve", grade, comment });
    approveMutation.mutate(documentId, {
      onSuccess: () => {
        toast.success(t.status.approved);
        setPendingAction(null);
        refetch();
      },
      onError: (err: any) => {
        toast.error(err?.response?.data?.detail ?? t.errors.approveFailed);
        setPendingAction(null);
      },
    });
  };

  const handleReject = (grade: number, comment: string) => {
    setPendingAction({ type: "reject", grade, comment });
    rejectMutation.mutate(
      { id: documentId, reason: comment || "Not meeting requirements." },
      {
        onSuccess: () => {
          toast.success(t.status.rejected);
          setPendingAction(null);
          refetch();
        },
        onError: (err: any) => {
          toast.error(err?.response?.data?.detail ?? t.errors.rejectFailed);
          setPendingAction(null);
        },
      }
    );
  };

  const handleNewVersion = async (file: File) => {
    setIsUploadingVersion(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      await apiClient.post(`/documents/${documentId}/new-version`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success(t.documents.uploadButton);
      refetch();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? t.errors.uploadFailed);
    } finally {
      setIsUploadingVersion(false);
    }
  };

  const handleExpire = async () => {
    setIsExpiring(true);
    try {
      await apiClient.post(`/documents/${documentId}/expire`);
      toast.success(t.status.expired);
      refetch();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? t.errors.generic);
    } finally {
      setIsExpiring(false);
    }
  };

  const handleRevectorize = async () => {
    setIsRevectorizing(true);
    try {
      await vectorizationApi.vectorize(documentId, true);
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
      await vectorizationApi.deleteVectors(documentId);
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

  if (isLoading) {
    return (
      <div className="p-8 flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-tertiary border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-on-surface-variant">{t.documents.detail.loading}</p>
        </div>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="p-8 flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="flex flex-col items-center gap-4 max-w-md text-center">
          <span
            className="material-symbols-outlined text-5xl text-error"
            style={{ fontSize: "48px" }}
          >
            error
          </span>
          <h2 className="text-xl font-bold text-on-surface">{t.documents.detail.notFound}</h2>
          <p className="text-sm text-on-surface-variant">
            {t.documents.detail.notFoundDesc.replace("{id}", documentId)}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-tertiary text-on-tertiary rounded-lg font-semibold text-sm"
          >
            {t.common.retry}
          </button>
        </div>
      </div>
    );
  }

  const sidebarData = mapDocumentToSidebar(
    { ...document, is_vectorized: vecStatus?.is_vectorized ?? document.is_vectorized },
    t
  );
  const userRole = deriveRole();
  const isPending = document.status === "pending_review";
  const isApproved = document.status === "approved";

  return (
    <div className="p-8 flex gap-8 h-[calc(100vh-4rem)] overflow-hidden">
      {/* Left: Document content */}
      <DocumentPreview
        title={document.title ?? document.original_filename ?? "Untitled"}
        description={document.description ?? t.documents.detail.noDescription}
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
                  (vecStatus?.is_vectorized ?? document.is_vectorized)
                    ? "bg-green-100 text-green-800"
                    : "bg-yellow-100 text-yellow-800"
                }`}
              >
                {(vecStatus?.is_vectorized ?? document.is_vectorized)
                  ? t.documents.detail.vectorized
                  : t.documents.detail.notVectorized}
              </span>
            </div>
            {document.download_url && (
              <div>
                <a
                  href={document.download_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 text-tertiary font-semibold text-sm hover:underline"
                >
                  <span className="material-symbols-outlined text-[18px]">download</span>
                  {t.documents.detail.downloadOriginal}
                </a>
              </div>
            )}
            {!(vecStatus?.is_vectorized ?? document.is_vectorized) && isPending && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-800">
                {t.documents.detail.notVectorizedNotice}
              </div>
            )}

            {/* Additional actions */}
            <div className="border-t border-surface-variant/30 pt-4 mt-4">
              <div className="flex flex-wrap gap-2">
                {userRole !== "viewer" && (
                  <>
                    <button
                      onClick={triggerNewVersionUpload}
                      disabled={isUploadingVersion}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-outline-variant/40 text-on-surface-variant hover:bg-surface-container-low transition-colors disabled:opacity-50"
                    >
                      <span className="material-symbols-outlined text-[16px]">upload</span>
                      {isUploadingVersion ? t.common.loading : t.documents.detail.newVersion}
                    </button>
                    <button
                      onClick={handleExpire}
                      disabled={isExpiring}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-outline-variant/40 text-on-surface-variant hover:bg-surface-container-low transition-colors disabled:opacity-50"
                    >
                      <span className="material-symbols-outlined text-[16px]">timer_off</span>
                      {isExpiring ? t.common.loading : t.documents.detail.expire}
                    </button>
                  </>
                )}
                {isApproved && (
                  <button
                    onClick={handleRevectorize}
                    disabled={isRevectorizing}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-outline-variant/40 text-on-surface-variant hover:bg-surface-container-low transition-colors disabled:opacity-50"
                  >
                    <span className="material-symbols-outlined text-[16px]">auto_awesome</span>
                    {isRevectorizing ? t.common.loading : t.documents.detail.revectorize}
                  </button>
                )}
                {isApproved && (vecStatus?.is_vectorized ?? document.is_vectorized) && (
                  <button
                    onClick={handleDeleteVectors}
                    disabled={isDeletingVectors}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-red-200 text-red-700 hover:bg-red-50 transition-colors disabled:opacity-50"
                  >
                    <span className="material-symbols-outlined text-[16px]">delete</span>
                    {isDeletingVectors ? t.common.loading : t.documents.detail.deleteVectors}
                  </button>
                )}
              </div>
            </div>
          </div>
        }
      />

      {/* Right: Sidebar with approval workflow */}
      <DocumentSidebar
        data={sidebarData}
        userRole={userRole}
        onApprove={handleApprove}
        onReject={handleReject}
        isApproving={approveMutation.isPending}
        isRejecting={rejectMutation.isPending}
      />
    </div>
  );
}
