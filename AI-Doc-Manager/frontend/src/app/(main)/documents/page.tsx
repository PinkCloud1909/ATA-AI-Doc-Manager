"use client";
import { useMemo, useState } from "react";
import { usePermission } from "@/hooks/usePermission";
import { useDocumentList } from "@/hooks/useDocuments";

import UploadForm from "@/components/documents/UploadForm";
import DocumentFilters from "@/components/documents/DocumentFilters";
import DocumentStats from "@/components/documents/DocumentStats";

import DocumentTable, {
  DocumentUserRole,
  DocumentItem,
} from "@/components/documents/DocumentTable";
import { DocumentListItem } from "@/types/document";

type RoleOverride = "auto" | DocumentUserRole;

const roleTesterEnabled = process.env.NEXT_PUBLIC_ENABLE_ROLE_TESTER === "true";

const roleOptions: Array<{ value: RoleOverride; label: string }> = [
  { value: "auto", label: "Auto" },
  { value: "viewer", label: "Viewer" },
  { value: "editor", label: "Editor" },
  { value: "approver", label: "Approver" },
];

function resolveDocumentUserRole(
  perm: ReturnType<typeof usePermission>,
): DocumentUserRole {
  if (perm.canApprove || perm.canAdmin) return "approver";
  if (perm.canUpload || perm.canReview) return "editor";
  return "viewer";
}

const statusLabels: Record<string, DocumentItem["status"]> = {
  approved: "Approved",
  pending_review: "Pending",
  draft: "Draft",
  expired: "Expired",
};

const typeLabels: Record<string, string> = {
  policy: "Policy",
  manual: "Manual",
  report: "Report",
  other: "Other",
};

const typeIcons: Record<
  string,
  Pick<DocumentItem, "icon" | "bgColor" | "iconColor">
> = {
  policy: {
    icon: "policy",
    bgColor: "bg-green-50",
    iconColor: "text-green-600",
  },
  manual: {
    icon: "menu_book",
    bgColor: "bg-blue-50",
    iconColor: "text-blue-600",
  },
  report: {
    icon: "description",
    bgColor: "bg-red-50",
    iconColor: "text-red-600",
  },
  other: {
    icon: "edit_document",
    bgColor: "bg-neutral-100",
    iconColor: "text-neutral-600",
  },
};

function formatUpdatedAt(value?: string) {
  if (!value) return "--";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--";

  return new Intl.DateTimeFormat("vi-VN", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}

function toDocumentItem(doc: DocumentListItem): DocumentItem {
  const type = String(doc.document_type ?? "other").toLowerCase();
  const iconConfig = typeIcons[type] ?? typeIcons.other;

  return {
    id: doc.document_id ?? doc.id ?? doc.original_filename,
    name: doc.title ?? doc.original_filename,
    category: typeLabels[type] ?? type,
    type: typeLabels[type] ?? type,
    status: statusLabels[String(doc.status).toLowerCase()] ?? "Draft",
    version: String(doc.version),
    score: "--",
    updatedAt: formatUpdatedAt(doc.created_at),
    author: doc.created_by_name ?? doc.created_by ?? "Không rõ",
    ...iconConfig,
  };
}

export default function DocumentsPage() {
  // 1. Khai báo State cho các bộ lọc
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("Tất cả");
  const [typeFilter, setTypeFilter] = useState("Tất cả");

  //3. State quản lý việc mở/đóng Modal Upload
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  const {
    data: documentList,
    isLoading: isLoadingDocuments,
    isError: isDocumentListError,
  } = useDocumentList({ page: 1, page_size: 100 });
  const documents = useMemo(
    () => (documentList?.items ?? []).map(toDocumentItem),
    [documentList],
  );

  const perm = usePermission();
  const inferredUserRole = resolveDocumentUserRole(perm);
  const [roleOverride, setRoleOverride] = useState<RoleOverride>("auto");
  const currentUserRole =
    roleTesterEnabled && roleOverride !== "auto"
      ? roleOverride
      : inferredUserRole;

  // 2. Logic Lọc dữ liệu (Real-time)
  const filteredDocs = documents.filter((doc) => {
    // Ép về chữ thường để tìm kiếm không phân biệt hoa thường
    const matchesSearch =
      doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.id.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === "Tất cả" || doc.status === statusFilter;
    const matchesType = typeFilter === "Tất cả" || doc.type === typeFilter;

    // Phải thỏa mãn CẢ 3 điều kiện mới được hiển thị
    return matchesSearch && matchesStatus && matchesType;
  });

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Page Header */}
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-1">
            <h2 className="text-3xl font-extrabold tracking-tight text-on-surface">
              Quản lý tài liệu
            </h2>
            <p className="text-on-surface-variant text-sm">
              Trung tâm lưu trữ và kiểm duyệt tri thức hệ thống Architect SOC.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
            {roleTesterEnabled && (
              <div
                className="inline-flex w-full rounded-lg bg-surface-container-low p-1 sm:w-auto"
                role="group"
                aria-label="Role kiểm thử"
                data-testid="documents-role-tester"
              >
                {roleOptions.map((option) => {
                  const isSelected = roleOverride === option.value;

                  return (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => setRoleOverride(option.value)}
                      className={`min-h-9 flex-1 rounded-lg px-3 text-xs font-bold uppercase tracking-wide transition-colors sm:flex-none ${
                        isSelected
                          ? "bg-white text-tertiary shadow-sm"
                          : "text-on-surface-variant hover:bg-white/60"
                      }`}
                    >
                      {option.label}
                    </button>
                  );
                })}
              </div>
            )}
            {currentUserRole !== "viewer" && (
              <button
                onClick={() => setIsUploadModalOpen(true)}
                className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 transition-colors rounded-lg text-sm font-medium text-white"
              >
                <span className="material-symbols-outlined text-sm">
                  upload_file
                </span>
                Tải lên
              </button>
            )}
          </div>
        </div>

        {/* Truyền State và hàm SetState xuống cho Filter */}
        <DocumentFilters
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          statusFilter={statusFilter}
          setStatusFilter={setStatusFilter}
          typeFilter={typeFilter}
          setTypeFilter={setTypeFilter}
        />

        {isDocumentListError && (
          <div className="rounded-lg bg-error-container/20 px-4 py-3 text-sm font-medium text-error">
            Không thể tải danh sách tài liệu từ backend. Vui lòng kiểm tra đăng
            nhập và quyền truy cập API.
          </div>
        )}

        {isLoadingDocuments ? (
          <div className="rounded-lg bg-surface-container-lowest px-6 py-10 text-center text-sm text-on-surface-variant">
            Đang tải danh sách tài liệu từ backend...
          </div>
        ) : (
          <DocumentTable documents={filteredDocs} userRole={currentUserRole} />
        )}

        <DocumentStats />
      </div>
      {/* Hiển thị Modal Upload */}
      {isUploadModalOpen && (
        <UploadForm onClose={() => setIsUploadModalOpen(false)} />
      )}
    </div>
  );
}
