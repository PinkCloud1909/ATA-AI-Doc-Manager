"use client"

import { useState } from "react"
import Link from "next/link"
import { useMutation } from "@tanstack/react-query"
import { toast } from "sonner"
import apiClient from "@/lib/api/client"
import { DocumentType } from "@/types/document"

interface GenerateResult {
  id: string
  document_id: string
  title: string
  file_link: string
  version: number
  output_format: "docx" | "pdf"
}

export default function GeneratePage() {
  const [prompt, setPrompt] = useState("")
  const [docType, setDocType] = useState<DocumentType>(DocumentType.MANUAL)
  const [outputFormat, setOutputFormat] = useState<"docx" | "pdf">("docx")
  const [result, setResult] = useState<GenerateResult | null>(null)

  const generate = useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post<GenerateResult>("/generate/runbook", {
        prompt,
        document_type: docType,
        output_format: outputFormat,
      })
      return data
    },
    onSuccess: (data) => {
      setResult(data)
      toast.success("Tài liệu đã được tạo và lưu thành công")
    },
    onError: () => toast.error("Tạo tài liệu thất bại"),
  })

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Tạo Runbook bằng AI</h1>
        <p className="mt-0.5 text-sm text-slate-500">
          Mô tả yêu cầu, chọn định dạng DOCX/PDF và lưu tài liệu vào hệ thống.
        </p>
      </div>

      <div className="space-y-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="grid gap-3 md:grid-cols-2">
          <div className="space-y-1">
            <label className="text-sm font-medium text-slate-700">Loại tài liệu</label>
            <select
              value={docType}
              onChange={(event) => setDocType(event.target.value as DocumentType)}
              className="block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={DocumentType.MANUAL}>Manual / Runbook</option>
              <option value={DocumentType.POLICY}>Policy</option>
              <option value={DocumentType.REPORT}>Report</option>
              <option value={DocumentType.OTHER}>Other</option>
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-slate-700">Định dạng</label>
            <select
              value={outputFormat}
              onChange={(event) => setOutputFormat(event.target.value as "docx" | "pdf")}
              className="block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="docx">DOCX</option>
              <option value="pdf">PDF</option>
            </select>
          </div>
        </div>

        <div className="space-y-1">
          <label className="text-sm font-medium text-slate-700">Mô tả yêu cầu runbook</label>
          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            rows={7}
            placeholder={`Ví dụ:\nViết runbook hướng dẫn quy trình xử lý sự cố thanh toán, bao gồm: xác định ảnh hưởng, kiểm tra log, rollback, thông báo và hậu kiểm.`}
            className="w-full resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="button"
          onClick={() => generate.mutate()}
          disabled={!prompt.trim() || generate.isPending}
          className="w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition-all hover:bg-blue-700 disabled:opacity-60"
        >
          {generate.isPending ? "Đang tạo tài liệu..." : "Tạo tài liệu"}
        </button>
      </div>

      {result && (
        <div className="space-y-3 rounded-xl border border-emerald-200 bg-emerald-50 p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-emerald-800">
            Tạo tài liệu thành công
          </h2>
          <p className="text-sm text-emerald-700">
            {result.title} · v{result.version} · {result.output_format.toUpperCase()}
          </p>
          <Link
            href={`/documents/${result.document_id ?? result.id}`}
            className="inline-flex rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-emerald-700"
          >
            Xem tài liệu
          </Link>
        </div>
      )}
    </div>
  )
}
