"use client";

import { usePendingApprovals } from "@/hooks/useDocuments";
import { StatusBadge } from "@/components/documents/StatusBadge";
import { ApprovalActions } from "@/components/approvals/ApprovalActions";
import Link from "next/link";

export function ApprovalQueue() {
  const { data: queue, isLoading } = usePendingApprovals();

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-14 bg-slate-100 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  if (!queue?.length) {
    return (
      <div className="py-8 text-center text-slate-400 text-sm">
        No pending approvals
      </div>
    );
  }

  return (
    <ul className="divide-y divide-slate-100">
      {queue.map((doc) => (
        <li
          key={doc.document_id}
          className="flex items-center justify-between px-5 py-4 gap-4 hover:bg-slate-50 transition-colors"
        >
          <div className="min-w-0 flex-1">
            <Link
              href={`/documents/${doc.document_id}`}
              className="font-medium text-slate-800 hover:text-blue-600 text-sm truncate block"
            >
              {doc.title}
            </Link>
            <p className="text-xs text-slate-400 mt-0.5">
              v{doc.version} · {doc.document_type} · {doc.submitted_by_name ?? doc.created_by_name ?? "Unknown user"}
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <StatusBadge status={doc.status} />
            <ApprovalActions documentId={doc.document_id} />
          </div>
        </li>
      ))}
    </ul>
  );
}
