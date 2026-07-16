"use client";

import { useTranslation, formatT } from "@/i18n/LanguageContext";
import { usePendingApprovals, useApproveDocument, useRejectDocument } from "@/hooks/useDocuments";
import { StatusBadge } from "@/components/documents/StatusBadge";
import { ApprovalActions } from "@/components/approvals/ApprovalActions";
import { useQueryClient } from "@tanstack/react-query";
import { approvalKeys } from "@/hooks/useDocuments";
import Link from "next/link";

export default function ApprovalsPage() {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const { data: queue, isLoading } = usePendingApprovals();

  const handleDone = () => {
    qc.invalidateQueries({ queryKey: approvalKeys.pending() });
  };

  return (
    <div className="space-y-6 min-w-0">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">{t.approvals.title}</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          {formatT(t.approvals.subtitle, { count: queue?.length ?? 0 })}
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden min-w-0">
        {isLoading ? (
          <div className="p-6 space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-14 bg-slate-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : !queue?.length ? (
          <div className="py-16 text-center text-slate-400 text-sm">
            {t.approvals.noPending}
          </div>
        ) : (
          <ul className="divide-y divide-slate-100">
            {queue.map((doc) => (
              <li
                key={doc.document_id}
                className="flex items-center justify-between px-5 py-4 gap-4 hover:bg-slate-50 transition-colors min-w-0"
              >
                <div className="min-w-0 flex-1">
                  <Link
                    href={`/documents/${doc.document_id}`}
                    className="font-medium text-slate-800 hover:text-blue-600 text-sm truncate block"
                  >
                    {doc.document_id}
                  </Link>
                  <p className="text-xs text-slate-400 mt-0.5">
                    v{doc.version} ·{" "}
                    {doc.submitted_at
                      ? new Date(doc.submitted_at).toLocaleDateString("vi-VN")
                      : ""}
                  </p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <StatusBadge status={doc.status} />
                  <ApprovalActions
                    documentId={doc.document_id}
                    onDone={handleDone}
                  />
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
