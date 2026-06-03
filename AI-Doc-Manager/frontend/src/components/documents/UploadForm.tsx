"use client"

import { FormEvent, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { AxiosError } from "axios"
import { toast } from "sonner"
import { UploadCloud } from "lucide-react"
import { useUploadDocument } from "@/hooks/useDocuments"
import { DocumentType } from "@/types/document"
import { formatFileSize, isDocx, isPdf } from "@/lib/gcs"

const TYPE_OPTIONS = [
  { value: DocumentType.REPORT, label: "Báo cáo" },
  { value: DocumentType.MANUAL, label: "Hướng dẫn / Runbook" },
  { value: DocumentType.POLICY, label: "Chính sách" },
  { value: DocumentType.OTHER, label: "Khác" },
]

const STAGE_LABEL = {
  idle: "",
  signing: "Đang chuẩn bị upload...",
  uploading: "Đang upload...",
  confirming: "Đang lưu metadata...",
}

interface UploadFormProps {
  onClose?: () => void
}

function getErrorMessage(error: unknown) {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail
    if (typeof detail === "string") return detail
    return error.message
  }
  if (error instanceof Error) return error.message
  return "Không upload được tài liệu. Kiểm tra backend rồi thử lại."
}

export default function UploadForm({ onClose }: UploadFormProps) {
  const router = useRouter()
  const inputRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [docType, setDocType] = useState<DocumentType>(DocumentType.REPORT)
  const [versionOf, setVersionOf] = useState("")
  const { mutateAsync, isPending, progress, stage } = useUploadDocument()

  const pickFile = (nextFile: File) => {
    if (!isPdf(nextFile.name) && !isDocx(nextFile.name)) {
      toast.error("Chỉ hỗ trợ PDF hoặc DOCX")
      return
    }
    setFile(nextFile)
    setTitle(nextFile.name.replace(/\.[^/.]+$/, ""))
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!file) {
      toast.error("Vui lòng chọn file")
      return
    }

    try {
      const doc = await mutateAsync({
        file,
        title,
        description,
        document_type: docType,
        document_group_id: versionOf.trim() || undefined,
      })
      toast.success(versionOf ? "Đã tạo version mới" : "Upload tài liệu thành công")
      onClose?.()
      router.push(`/documents/${doc.id}`)
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
  }

  return (
    <form onSubmit={submit} className="space-y-5">
      {onClose && (
        <div className="flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="rounded-md px-2 py-1 text-sm text-slate-500 hover:bg-slate-100"
          >
            Đóng
          </button>
        </div>
      )}

      <div
        onClick={() => inputRef.current?.click()}
        className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-300 px-6 py-10 text-center transition-colors hover:border-blue-500 hover:bg-blue-50"
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(event) => {
            const selected = event.target.files?.[0]
            if (selected) pickFile(selected)
          }}
        />
        <UploadCloud className="mb-3 h-10 w-10 text-blue-600" />
        {file ? (
          <>
            <p className="text-sm font-semibold text-slate-800">{file.name}</p>
            <p className="mt-1 text-xs text-slate-500">{formatFileSize(file.size)}</p>
          </>
        ) : (
          <>
            <p className="text-sm font-semibold text-slate-800">
              Chọn file PDF/DOCX để upload
            </p>
            <p className="mt-1 text-xs text-slate-500">
              File sẽ được lưu qua backend object storage adapter
            </p>
          </>
        )}
      </div>

      <div className="space-y-1">
        <label className="text-sm font-medium text-slate-700">Tên tài liệu</label>
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          placeholder="Nhập tên tài liệu"
        />
      </div>

      <div className="space-y-1">
        <label className="text-sm font-medium text-slate-700">Loại tài liệu</label>
        <select
          value={docType}
          onChange={(event) => setDocType(event.target.value as DocumentType)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          {TYPE_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-1">
        <label className="text-sm font-medium text-slate-700">
          Tạo version mới cho document id
        </label>
        <input
          value={versionOf}
          onChange={(event) => setVersionOf(event.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 font-mono text-sm"
          placeholder="Để trống nếu upload tài liệu mới"
        />
      </div>

      <div className="space-y-1">
        <label className="text-sm font-medium text-slate-700">Mô tả</label>
        <textarea
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          rows={3}
        />
      </div>

      {isPending && (
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-slate-600">
            <span>{STAGE_LABEL[stage]}</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2 rounded-full bg-slate-200">
            <div
              className="h-2 rounded-full bg-blue-600 transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      <button
        type="submit"
        disabled={isPending || !file}
        className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:opacity-60"
      >
        {isPending ? "Đang xử lý..." : "Upload tài liệu"}
      </button>
    </form>
  )
}
