"use client"

import Link from "next/link"
import { useMemo, useState } from "react"
import { Plus, Upload } from "lucide-react"
import { useDocumentList } from "@/hooks/useDocuments"
import DocumentTable from "@/components/documents/DocumentTable"
import { DocumentStatus, DocumentType } from "@/types/document"

const STATUS_OPTIONS = [
  { value: "", label: "Tất cả trạng thái" },
  { value: DocumentStatus.DRAFT, label: "Draft" },
  { value: DocumentStatus.PENDING_REVIEW, label: "Pending Review" },
  { value: DocumentStatus.APPROVED, label: "Approved" },
  { value: DocumentStatus.REJECTED, label: "Rejected" },
  { value: DocumentStatus.EXPIRED, label: "Expired" },
]

const TYPE_OPTIONS = [
  { value: "", label: "Tất cả loại" },
  { value: DocumentType.POLICY, label: "Policy" },
  { value: DocumentType.MANUAL, label: "Manual / Runbook" },
  { value: DocumentType.REPORT, label: "Report" },
  { value: DocumentType.OTHER, label: "Other" },
]

export default function DocumentsPage() {
  const [search, setSearch] = useState("")
  const [status, setStatus] = useState("")
  const [type, setType] = useState("")

  const params = useMemo(
    () => ({
      page: 1,
      page_size: 100,
      search: search.trim() || undefined,
      status: (status || undefined) as DocumentStatus | undefined,
      document_type: (type || undefined) as DocumentType | undefined,
    }),
    [search, status, type],
  )

  const { data, isLoading, error, refetch } = useDocumentList(params)

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <div className="mx-auto max-w-7xl space-y-8">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div className="space-y-1">
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">
              Quản lý tài liệu
            </h1>
            <p className="text-sm text-slate-500">
              Upload, versioning, chấm điểm và phê duyệt tài liệu.
            </p>
          </div>
          <div className="flex gap-2">
            <Link
              href="/generate"
              className="inline-flex items-center gap-2 rounded-lg border border-blue-200 px-4 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-50"
            >
              <Plus size={16} />
              Tạo tài liệu
            </Link>
            <Link
              href="/documents/upload"
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
            >
              <Upload size={16} />
              Upload
            </Link>
          </div>
        </div>

        <div className="grid gap-3 rounded-xl border border-slate-100 bg-white p-4 shadow-sm md:grid-cols-[1fr_220px_180px_auto]">
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Tìm theo tên tài liệu..."
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          >
            {STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <select
            value={type}
            onChange={(event) => setType(event.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          >
            {TYPE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => refetch()}
            className="rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200"
          >
            Làm mới
          </button>
        </div>

        {error && (
          <div className="rounded-lg border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
            Không tải được danh sách tài liệu. Kiểm tra backend ở port 8000.
          </div>
        )}

        <DocumentTable items={data?.items ?? []} isLoading={isLoading} />
      </div>
    </div>
  )
}
