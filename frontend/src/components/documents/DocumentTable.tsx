"use client";

import { useState } from "react";
import { useTranslation, formatT } from "@/i18n/LanguageContext";
import { StatusBadge } from "./StatusBadge";
import { documentsApi } from "@/lib/api/documents";
import type { DocumentListItem, DocumentType } from "@/types/document";

interface DocumentTableProps {
  documents: DocumentListItem[];
  userRole: string;
}

const TYPE_ICONS: Record<DocumentType, { icon: string; bg: string; color: string }> = {
  policy: { icon: "policy", bg: "bg-purple-50", color: "text-purple-600" },
  manual: { icon: "menu_book", bg: "bg-blue-50", color: "text-blue-600" },
  report: { icon: "assessment", bg: "bg-orange-50", color: "text-orange-600" },
  other: { icon: "description", bg: "bg-neutral-100", color: "text-neutral-600" },
};

function formatDate(value?: string | null): string {
  if (!value) return "--";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "--";
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(d);
}

/** Row-level "View" button — fetches the signed URL then opens in a new tab */
function ViewButton({ documentId }: { documentId: string }) {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);

  const handleView = async () => {
    setLoading(true);
    try {
      // 1. Request the document detail from the backend.
      //    The backend validates permissions and returns a time-limited
      //    presigned download_url in DocumentDetailResponse.
      const doc = await documentsApi.getById(documentId);

      // 2. Open the signed URL in a new tab.
      if (doc.download_url) {
        window.open(doc.download_url, "_blank", "noopener,noreferrer");
      }
    } catch {
      // If getById fails, fall back to the detail page so the user
      // can see the specific error (e.g. 403, 404).
      window.location.href = `/documents/${documentId}`;
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleView}
      disabled={loading}
      className="p-2 hover:bg-surface-container-low rounded-lg text-neutral-500 transition-colors inline-flex items-center justify-center disabled:opacity-50"
      title={t.common.view}
    >
      {loading ? (
        <span className="inline-block w-[18px] h-[18px] border-2 border-neutral-400 border-t-transparent rounded-full animate-spin" />
      ) : (
        <span className="material-symbols-outlined text-[18px]">visibility</span>
      )}
    </button>
  );
}

export default function DocumentTable({
  documents,
  userRole,
}: DocumentTableProps) {
  const { t } = useTranslation();

  return (
    <div className="bg-surface-container-lowest rounded-2xl overflow-hidden shadow-sm border border-transparent">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="bg-surface-container-low/50">
            <th className="px-6 py-4 text-[11px] font-bold uppercase tracking-widest text-neutral-400">
              {t.documents.table.documentName}
            </th>
            <th className="px-6 py-4 text-[11px] font-bold uppercase tracking-widest text-neutral-400">
              {t.documents.table.status}
            </th>
            <th className="px-6 py-4 text-[11px] font-bold uppercase tracking-widest text-neutral-400 text-center">
              {t.documents.table.version}
            </th>
            <th className="px-6 py-4 text-[11px] font-bold uppercase tracking-widest text-neutral-400">
              {t.documents.table.updated}
            </th>
            <th className="px-6 py-4 text-[11px] font-bold uppercase tracking-widest text-neutral-400 text-right">
              {t.documents.table.actions}
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-container-low">
          {documents.length === 0 ? (
            <tr>
              <td colSpan={5} className="px-6 py-10 text-center text-on-surface-variant">
                {t.documents.table.noDocuments}
              </td>
            </tr>
          ) : (
            documents.map((doc) => {
              const dt = doc.document_type as DocumentType;
              const iconCfg = TYPE_ICONS[dt] ?? TYPE_ICONS.other;
              return (
                <tr
                  key={doc.document_id}
                  className="hover:bg-surface-container-low/30 transition-colors group"
                >
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-10 h-10 rounded-lg ${iconCfg.bg} flex items-center justify-center ${iconCfg.color}`}
                      >
                        <span className="material-symbols-outlined">{iconCfg.icon}</span>
                      </div>
                      <div>
                        <p className="font-semibold text-sm text-on-surface">
                          {doc.title}
                        </p>
                        <p className="text-[11px] text-neutral-400">
                          {doc.original_filename}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <StatusBadge status={doc.status} />
                  </td>
                  <td className="px-6 py-5 text-center">
                    <span className="text-xs font-mono bg-surface-container-low px-2 py-0.5 rounded">
                      v{doc.version}
                    </span>
                  </td>
                  <td className="px-6 py-5">
                    <p className="text-xs text-on-surface">
                      {formatDate(doc.created_at)}
                    </p>
                  </td>
                  <td className="px-6 py-5">
                    <div className="flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <ViewButton documentId={doc.document_id} />
                    </div>
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>

      <div className="px-6 py-4 flex items-center justify-between border-t border-surface-container-low bg-white">
        <p className="text-xs text-neutral-500 font-medium">
          {formatT(t.documents.table.totalCount, { count: documents.length })}
        </p>
        <div className="flex items-center gap-2">
          <button
            className="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-400 hover:bg-neutral-50 transition-colors disabled:opacity-50"
            disabled
          >
            <span className="material-symbols-outlined text-[18px]">chevron_left</span>
          </button>
          <button className="w-8 h-8 rounded-lg flex items-center justify-center bg-tertiary text-on-tertiary text-xs font-bold">
            1
          </button>
          <button className="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-400 hover:bg-neutral-50 transition-colors">
            <span className="material-symbols-outlined text-[18px]">chevron_right</span>
          </button>
        </div>
      </div>
    </div>
  );
}
