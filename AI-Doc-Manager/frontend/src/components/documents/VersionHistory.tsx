"use client";

import { useDocumentList } from "@/hooks/useDocuments";
import { StatusBadge } from "./StatusBadge";
import Link from "next/link";

interface Props {
  documentGroupId: string;
  currentDocumentId: string;
}

export function VersionHistory({ documentGroupId, currentDocumentId }: Props) {
  // Note: The API doesn't have a dedicated version-history endpoint.
  // We approximate by listing all docs and filtering by document_group_id client-side.
  const { data, isLoading } = useDocumentList({ page_size: 100 });

  const versions = (data?.items ?? []).filter(
    (d) => d.document_group_id === documentGroupId,
  );

  if (isLoading)
    return <p className="text-sm text-slate-400">Loading history…</p>;
  if (!versions.length) return null;

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-slate-700">
        Version History
      </h3>
      <ul className="space-y-1.5">
        {[...versions]
          .sort((a, b) => b.version - a.version)
          .map((v) => {
            const isCurrent = v.document_id === currentDocumentId;
            return (
              <li
                key={v.document_id}
                className={`flex items-center justify-between rounded-lg border px-3 py-2 text-sm ${
                  isCurrent
                    ? "border-blue-200 bg-blue-50"
                    : "border-slate-200 bg-white hover:border-slate-300"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`font-mono font-semibold ${
                      isCurrent ? "text-blue-700" : "text-slate-600"
                    }`}
                  >
                    v{v.version}
                  </span>
                  {isCurrent && (
                    <span className="text-xs text-blue-500 font-medium">
                      Current
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-3">
                  <StatusBadge status={v.status} />
                  <span className="text-xs text-slate-400">
                    {v.created_at
                      ? new Date(v.created_at).toLocaleDateString("vi-VN")
                      : ""}
                  </span>
                  {!isCurrent && (
                    <Link
                      href={`/documents/${v.document_id}`}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      View
                    </Link>
                  )}
                </div>
              </li>
            );
          })}
      </ul>
    </div>
  );
}
