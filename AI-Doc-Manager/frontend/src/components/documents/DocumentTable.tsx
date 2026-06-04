"use client"

import Link from "next/link"
import { FileText } from "lucide-react"
import { DocumentListItem, DocumentType } from "@/types/document"
import { StatusBadge } from "./StatusBadge"

const TYPE_LABEL: Record<DocumentType, string> = {
  [DocumentType.POLICY]: "Policy",
  [DocumentType.MANUAL]: "Manual / Runbook",
  [DocumentType.REPORT]: "Report",
  [DocumentType.OTHER]: "Other",
}

interface Props {
  items: DocumentListItem[]
  isLoading?: boolean
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export default function DocumentTable({ items, isLoading = false }: Props) {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-100 bg-white shadow-sm">
      <table className="w-full border-collapse text-left">
        <thead>
          <tr className="bg-slate-50">
            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400">
              Tên tài liệu
            </th>
            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400">
              Trạng thái
            </th>
            <th className="px-6 py-4 text-center text-xs font-bold uppercase tracking-wider text-slate-400">
              Version
            </th>
            <th className="px-6 py-4 text-center text-xs font-bold uppercase tracking-wider text-slate-400">
              Điểm
            </th>
            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400">
              Cập nhật
            </th>
            <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider text-slate-400">
              Hành động
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {isLoading ? (
            Array.from({ length: 4 }).map((_, index) => (
              <tr key={index}>
                <td colSpan={6} className="px-6 py-4">
                  <div className="h-12 animate-pulse rounded-lg bg-slate-100" />
                </td>
              </tr>
            ))
          ) : items.length === 0 ? (
            <tr>
              <td colSpan={6} className="px-6 py-12 text-center text-sm text-slate-400">
                Không có tài liệu phù hợp.
              </td>
            </tr>
          ) : (
            items.map((doc) => (
              <tr key={doc.id} className="transition-colors hover:bg-slate-50">
                <td className="px-6 py-5">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                      <FileText size={18} />
                    </div>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-slate-800">
                        {doc.title || doc.original_filename}
                      </p>
                      <p className="mt-0.5 text-xs text-slate-400">
                        {TYPE_LABEL[doc.document_type]} · {doc.original_filename}
                      </p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-5">
                  <StatusBadge status={doc.status} />
                </td>
                <td className="px-6 py-5 text-center">
                  <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-xs text-slate-700">
                    v{doc.version}
                  </span>
                </td>
                <td className="px-6 py-5 text-center">
                  <span className="text-sm font-semibold text-slate-700">
                    {doc.avg_grade != null ? doc.avg_grade.toFixed(1) : "--"}
                  </span>
                </td>
                <td className="px-6 py-5">
                  <p className="text-xs text-slate-700">{formatDate(doc.created_at)}</p>
                  <p className="mt-0.5 text-xs text-slate-400">
                    bởi {doc.created_by_name || "admin"}
                  </p>
                </td>
                <td className="px-6 py-5 text-right">
                  <Link
                    href={`/documents/${doc.id}`}
                    className="rounded-lg px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50"
                  >
                    Xem
                  </Link>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
