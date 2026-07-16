"use client";
import { useMemo, useState } from "react";
import { usePermission } from "@/hooks/usePermission";
import { useDocumentList } from "@/hooks/useDocuments";
import { useTranslation } from "@/i18n/LanguageContext";

import UploadForm from "@/components/documents/UploadForm";
import DocumentFilters from "@/components/documents/DocumentFilters";
import DocumentStats from "@/components/documents/DocumentStats";
import DocumentTable from "@/components/documents/DocumentTable";
import type { DocumentListItem } from "@/types/document";

export default function DocumentsPage() {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState(t.common.all);
  const [typeFilter, setTypeFilter] = useState(t.common.all);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  const {
    data: documentList,
    isLoading: isLoadingDocuments,
    isError: isDocumentListError,
  } = useDocumentList({ page: 1, page_size: 100 });

  const perm = usePermission();

  const documents = useMemo(
    () => documentList?.items ?? [],
    [documentList],
  );

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch =
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.document_id.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === t.common.all || doc.status === statusFilter;
    const matchesType =
      typeFilter === t.common.all || doc.document_type === typeFilter;

    return matchesSearch && matchesStatus && matchesType;
  });

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Page Header */}
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-1">
            <h2 className="text-3xl font-extrabold tracking-tight text-on-surface">
              {t.documents.title}
            </h2>
            <p className="text-on-surface-variant text-sm">
              {t.documents.subtitle}
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
            {perm.canUpload && (
              <button
                onClick={() => setIsUploadModalOpen(true)}
                className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 transition-colors rounded-lg text-sm font-medium text-white"
              >
                <span className="material-symbols-outlined text-sm">
                  upload_file
                </span>
                {t.documents.uploadButton}
              </button>
            )}
          </div>
        </div>

        <DocumentFilters
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          statusFilter={statusFilter}
          setStatusFilter={setStatusFilter}
          typeFilter={typeFilter}
          setTypeFilter={setTypeFilter}
        />

        {isDocumentListError && (
          <div className="rounded-lg bg-red-100 px-4 py-3 text-sm font-medium text-red-700">
            {t.errors.cannotLoadDocuments}
          </div>
        )}

        {isLoadingDocuments ? (
          <div className="rounded-lg bg-surface-container-lowest px-6 py-10 text-center text-sm text-on-surface-variant">
            {t.common.loading}
          </div>
        ) : (
          <DocumentTable
            documents={filteredDocs}
            userRole={perm.roleNames.includes("admin") ? "admin" : perm.canApprove ? "reviewer" : perm.canUpload ? "editor" : "viewer"}
          />
        )}

        <DocumentStats />
      </div>
      {isUploadModalOpen && (
        <UploadForm onClose={() => setIsUploadModalOpen(false)} />
      )}
    </div>
  );
}
