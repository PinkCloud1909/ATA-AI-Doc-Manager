"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useDocument, useDownloadUrl } from "@/hooks/useDocuments";
import { StatusBadge } from "@/components/documents/StatusBadge";
import { VersionHistory } from "@/components/documents/VersionHistory";
import { ReviewForm } from "@/components/documents/ReviewForm";
import { ApprovalActions } from "@/components/approvals/ApprovalActions";
import { usePermission } from "@/hooks/usePermission";
import { DocumentStatus } from "@/types/document";
import { gcsFilename, formatFileSize, isPdf } from "@/lib/gcs";
/*
export default function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const perm   = usePermission()
  const { data: doc, isLoading } = useDocument(id)

  // Lazy fetch Signed Download URL (GCS private bucket)
  const [wantDownload, setWantDownload] = useState(false)
  const { data: downloadUrl, isLoading: loadingUrl } = useDownloadUrl(id, wantDownload)

  // Trigger download khi URL sẵn sàng
  const handleDownload = async () => {
    setWantDownload(true)
    // URL sẽ load qua React Query; effect bên dưới mở tab
  }

  // Mở URL khi đã có
  if (downloadUrl && wantDownload) {
    window.open(downloadUrl, "_blank")
    setWantDownload(false)
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-16 bg-slate-100 rounded-xl animate-pulse" />
        ))}
      </div>
    )
  }

  if (!doc) return <p className="text-slate-400 text-sm">Không tìm thấy tài liệu.</p>

  const filename = doc.original_filename || gcsFilename(doc.file_link)
  const isDraft   = doc.status === DocumentStatus.DRAFT
  const isPending = doc.status === DocumentStatus.PENDING_REVIEW

  return (
    <div className="max-w-4xl space-y-6">
      {/* Header */ /*}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{isPdf(filename) ? "📄" : "📝"}</span>
            <h1 className="text-xl font-bold text-slate-800 font-mono">{filename}</h1>
            <StatusBadge status={doc.status} />
          </div>
          <p className="text-sm text-slate-400">
            v{doc.version} · {doc.created_by_name} ·{" "}
            {new Date(doc.created_at).toLocaleDateString("vi-VN")}
            {doc.size_bytes && ` · ${formatFileSize(doc.size_bytes)}`}
          </p>
        </div>

        <div className="flex gap-2 flex-wrap">
          {/* GCS Download */ /*}
          <button
            onClick={handleDownload}
            disabled={loadingUrl}
            className="px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 text-slate-700
                       rounded-lg transition-colors disabled:opacity-50"
          >
            {loadingUrl ? "Đang tạo link…" : "Tải xuống ↓"}
          </button>

          {(isDraft || isPending) && (perm.canApprove || perm.canUpload) && (
            <ApprovalActions documentId={doc.id} />
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Metadata */ /*}
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <h2 className="text-sm font-semibold text-slate-700 mb-3">Thông tin</h2>
            <dl className="grid grid-cols-2 gap-3 text-sm">
              {[
                ["Loại tài liệu", doc.document_type],
                ["Phiên bản",     `v${doc.version}`],
                ["Content Type",  doc.content_type],
                ["Kích thước",    doc.size_bytes ? formatFileSize(doc.size_bytes) : "—"],
                ["Ngày tạo",      new Date(doc.created_at).toLocaleDateString("vi-VN")],
                ["Ngày sửa",      doc.modified_date ? new Date(doc.modified_date).toLocaleDateString("vi-VN") : "—"],
                ["Vertex AI",     doc.is_vectorized ? "✓ Đã index" : "✗ Chưa index"],
                ["Điểm TB",       doc.avg_grade != null ? `${doc.avg_grade.toFixed(1)} / 10` : "—"],
              ].map(([k, v]) => (
                <div key={k}>
                  <dt className="text-slate-400 text-xs">{k}</dt>
                  <dd className="font-medium text-slate-700 mt-0.5">{v}</dd>
                </div>
              ))}
            </dl>

            {/* GCS path */ /*}
            <div className="mt-4 pt-4 border-t border-slate-100">
              <dt className="text-slate-400 text-xs mb-1">GCS Path</dt>
              <dd className="font-mono text-xs text-slate-500 break-all">{doc.file_link}</dd>
            </div>
          </div>

          {/* Reviews */ /*}
          {doc.reviews && doc.reviews.length > 0 && (
            <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-3">
              <h2 className="text-sm font-semibold text-slate-700">
                Đánh giá ({doc.reviews.length})
              </h2>
              {doc.reviews.map((r) => (
                <div key={r.id} className="border-t border-slate-100 pt-3 first:border-0 first:pt-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-700">
                      {r.reviewer_name ?? "Reviewer"}
                    </span>
                    <span className={`text-sm font-bold ${
                      r.grade >= 7 ? "text-emerald-600" :
                      r.grade >= 5 ? "text-amber-500" : "text-red-500"
                    }`}>
                      {r.grade}/10
                    </span>
                  </div>
                  <p className="text-sm text-slate-500 mt-1">{r.comment}</p>
                </div>
              ))}
            </div>
          )}

          {perm.canReview && <ReviewForm documentId={doc.id} />}
        </div>

        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <VersionHistory groupId={doc.document_group_id} currentDocumentId={doc.id} />
          </div>
        </div>
      </div>
    </div>
  )
}
*/

import DocumentPreview from "@/components/documents/DocumentPreview";
import DocumentSidebar, {
  DocumentDetailData,
} from "@/components/documents/DocumentSidebar";
import React from "react";

// === DỮ LIỆU MOCK THEO TỪNG ID TÀI LIỆU ===
const MOCK_DOCUMENTS: Record<
  string,
  { preview: any; sidebar: DocumentDetailData }
> = {
  "DOC-2024-001": {
    preview: {
      title: "Kế Hoạch Ứng Phó Sự Cố v4",
      description:
        "Tài liệu này trình bày các quy trình tiêu chuẩn để xử lý các sự cố an ninh mạng trong tổ chức.",
      content: (
        <>
          <h2 className="text-2xl font-headline font-semibold mt-8 mb-4">
            1. Mục Đích
          </h2>
          <p>
            Cung cấp khuôn khổ có cấu trúc và có hệ thống để phát hiện, phân
            tích, ngăn chặn sự cố an ninh mạng.
          </p>
          <div className="bg-surface-container-low p-6 rounded-lg my-6 border-l-4 border-tertiary">
            <h3 className="font-headline font-semibold text-lg mb-2">
              Lưu ý Quan Trọng
            </h3>
            <p className="text-sm text-on-surface-variant">
              Liên hệ ngay với Trưởng nhóm SOC qua số khẩn cấp nội bộ khi có sự
              cố P1.
            </p>
          </div>
        </>
      ),
    },
    sidebar: {
      id: "DOC-2024-001",
      title: "Kế Hoạch Ứng Phó Sự Cố",
      status: "Bản Nháp",
      version: "v4.2.1",
      aiAssessment: {
        score: "8.5",
        label: "Khá Tốt",
        summary: "Cấu trúc rõ ràng, cần bổ sung chi tiết về phần phục hồi.",
        points: [
          {
            isPositive: true,
            text: "Phần 'Phạm Vi' được định nghĩa rất rõ ràng.",
          },
          {
            isPositive: false,
            text: "Cần chỉ định rõ thời gian cho bước 'Phục Hồi'.",
          },
        ],
      },
      reviewer: {
        name: "Trần Văn A",
        role: "Quản lý SOC",
        avatar:
          "https://lh3.googleusercontent.com/aida-public/AB6AXuA2hOD2ai6ZAcHaRwwVMTFaZe4-ihmKeOTfmGE8eNUcW3jwr7MUOy6mvsXmA_kaKNClwhR0d7f1W3kVC3M-1twZfS2wIKgkB5_D0UKxoAvqXYETbrPu1L-4hdKiM3wVS3S9Juc7Oxd6XF57XT5_njBbmGdsvXC3-mTc1z_N18HT0ejboaPJQ60mqZ4MxYuzkYo0ep7H-kPpYGwv-Ar-Ktk1Xo_T-MSGDy7rXTcwbKXz4cruGtgAhJgfVnuH_x881xRVCtXbUnRpzhmi",
        comment:
          "Vui lòng cập nhật số điện thoại khẩn cấp. Nó đã thay đổi vào tháng trước.",
        statusLabel: "Chờ Chỉnh Sửa",
      },
    },
  },
  "DOC-2024-042": {
    preview: {
      title: "Cloud Architecture Guideline",
      description: "Tiêu chuẩn thiết kế hạ tầng Cloud cho các dự án nội bộ.",
      content: (
        <>
          <h2 className="text-2xl font-headline font-semibold mt-8 mb-4">
            1. Kiến Trúc Mạng
          </h2>
          <p>
            Tất cả các dịch vụ nội bộ phải được đặt trong Private Subnet và giao
            tiếp qua VPC Peering.
          </p>
          <ul className="list-disc pl-6 space-y-2 mt-4">
            <li>Không mở public IP cho Database.</li>
            <li>Sử dụng NAT Gateway cho các truy cập ra ngoài internet.</li>
          </ul>
        </>
      ),
    },
    sidebar: {
      id: "DOC-2024-042",
      title: "Cloud Guideline",
      status: "Pending",
      version: "v1.0.5",
      aiAssessment: {
        score: "7.2",
        label: "Cần Cải Thiện",
        summary: "Thiếu phần cấu hình IAM Roles và bảo mật lưu trữ.",
        points: [
          {
            isPositive: true,
            text: "Kiến trúc mạng an toàn, tuân thủ AWS Well-Architected.",
          },
          {
            isPositive: false,
            text: "Thiếu hướng dẫn phân quyền IAM Role cho EKS.",
          },
        ],
      },
      reviewer: {
        name: "Minh Tú",
        role: "Cloud Architect",
        avatar:
          "https://lh3.googleusercontent.com/aida-public/AB6AXuA2hOD2ai6ZAcHaRwwVMTFaZe4-ihmKeOTfmGE8eNUcW3jwr7MUOy6mvsXmA_kaKNClwhR0d7f1W3kVC3M-1twZfS2wIKgkB5_D0UKxoAvqXYETbrPu1L-4hdKiM3wVS3S9Juc7Oxd6XF57XT5_njBbmGdsvXC3-mTc1z_N18HT0ejboaPJQ60mqZ4MxYuzkYo0ep7H-kPpYGwv-Ar-Ktk1Xo_T-MSGDy7rXTcwbKXz4cruGtgAhJgfVnuH_x881xRVCtXbUnRpzhmi",
        comment:
          "Vui lòng bổ sung phần IAM Roles và hướng dẫn bảo mật S3 Bucket.",
        statusLabel: "Chờ Chỉnh Sửa",
      },
    },
  },
};

// Hàm sinh dữ liệu dự phòng cho các ID không có sẵn trong Mock Data
const getDocumentData = (id: string) => {
  if (MOCK_DOCUMENTS[id]) return MOCK_DOCUMENTS[id];

  // Dữ liệu Fallback
  return {
    preview: {
      title: `Tài Liệu Cấu Hình ${id}`,
      description: `Tài liệu tự động tạo để hiển thị cho ID: ${id}`,
      content: (
        <>
          <h2 className="text-2xl font-headline font-semibold mt-8 mb-4">
            Nội Dung Đang Cập Nhật
          </h2>
          <p>
            Chưa có dữ liệu chi tiết cho tài liệu này trên hệ thống. Vui lòng
            liên hệ người tạo tài liệu để biết thêm chi tiết.
          </p>
        </>
      ),
    },
    sidebar: {
      id: id,
      title: `Tài liệu ${id}`,
      status: "Draft",
      version: "v1.0.0",
      aiAssessment: {
        score: "--",
        label: "Chưa Đánh Giá",
        summary: "Tài liệu mới, AI Curator chưa tiến hành phân tích.",
        points: [],
      },
      reviewer: null,
    },
  };
};

// Cập nhật Type cho params dưới dạng Promise (Next.js 15+)
interface PageProps {
  params: Promise<{ id: string }>;
}

// Chuyển Component thành async function
export default async function DocumentDetailPage({ params }: PageProps) {
  // Await params để lấy ID thực tế
  const resolvedParams = await params;
  const documentId = resolvedParams.id;

  // Lấy dữ liệu document (sẽ luôn lấy được nhờ hàm Fallback)
  const docData = getDocumentData(documentId);

  return (
    <div className="p-8 flex gap-8 h-[calc(100vh-4rem)] overflow-hidden">
      {/* Truyền Props xuống DocumentPreview */}
      <DocumentPreview
        title={docData.preview.title}
        description={docData.preview.description}
        content={docData.preview.content}
      />

      {/* Truyền Props xuống DocumentSidebar */}
      <DocumentSidebar data={docData.sidebar} />
    </div>
  );
}
