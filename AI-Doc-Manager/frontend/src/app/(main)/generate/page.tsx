"use client"

import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import apiClient from "@/lib/api/client"
import { DocumentType } from "@/types/document"
import { toast } from "sonner"
import Link from "next/link"

interface GenerateResult {
  id:        string
  file_link: string
  version:   number
}

export default function GeneratePage() {
  const [prompt,  setPrompt]  = useState("")
  const [docType, setDocType] = useState<DocumentType>(DocumentType.COMMON_GUIDE)
  const [result,  setResult]  = useState<GenerateResult | null>(null)

  const generate = useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post<GenerateResult>("/generate/runbook", {
        prompt,
        document_type: docType,
      })
      return data
    },
    onSuccess: (data) => {
      setResult(data)
      toast.success("Tài liệu đã được tạo và lưu thành công!")
    },
    onError: () => toast.error("Tạo tài liệu thất bại"),
  })

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Tạo Runbook bằng AI</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Mô tả yêu cầu — Gemini sẽ sinh nội dung và xuất file DOCX/PDF, lưu vào hệ thống
        </p>
      </div>

      {/* Form */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-5">
        <div className="space-y-1">
          <label className="text-sm font-medium text-slate-700">Loại tài liệu</label>
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value as DocumentType)}
            className="block w-full px-3 py-2 text-sm border border-slate-300 rounded-lg
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
          >
            <option value={DocumentType.COMMON_GUIDE}>Hướng dẫn chung</option>
            <option value={DocumentType.TEMPLATE}>Template</option>
            <option value={DocumentType.CUSTOMER_SPECIFIC}>Tài liệu khách hàng</option>
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-sm font-medium text-slate-700">
            Mô tả yêu cầu runbook
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={6}
            placeholder={`Ví dụ:\nViết runbook hướng dẫn quy trình deploy ứng dụng FastAPI lên Kubernetes,\nbao gồm: chuẩn bị môi trường, build Docker image, apply manifest, health check.`}
            className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
          />
        </div>

        <button
          onClick={() => generate.mutate()}
          disabled={!prompt.trim() || generate.isPending}
          className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-60
                     text-white text-sm font-semibold rounded-lg transition-all duration-200
                     shadow-lg shadow-blue-600/20 hover:shadow-xl hover:shadow-blue-600/30"
        >
          {generate.isPending ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Đang tạo tài liệu…
            </span>
          ) : (
            "✦ Tạo Runbook"
          )}
        </button>
      </div>

      {/* Result */}
      {result && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 space-y-3 shadow-sm">
          <h2 className="text-sm font-semibold text-emerald-800">
            ✓ Tài liệu đã được tạo thành công
          </h2>
          <div className="flex gap-3">
            <a
              href={result.file_link}
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2 bg-white border border-emerald-300 text-emerald-700
                         text-sm font-medium rounded-lg hover:bg-emerald-50 transition-colors"
            >
              Tải xuống ↓
            </a>
            <Link
              href={`/documents/${result.id}`}
              className="px-4 py-2 bg-emerald-600 text-white text-sm font-medium
                         rounded-lg hover:bg-emerald-700 transition-colors"
            >
              Xem tài liệu →
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
