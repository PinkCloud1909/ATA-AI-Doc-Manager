"use client";

import React, { useState, ChangeEvent, FormEvent, useRef } from "react";
import { useRouter } from "next/navigation";
import { useUploadDocument } from "@/hooks/useDocuments";
import { DocumentType } from "@/types/document";
import { formatFileSize, isPdf, isDocx } from "@/lib/gcs";
import { toast } from "sonner";

/*
const TYPE_OPTIONS = [
  { value: DocumentType.TEMPLATE,          label: "Template" },
  { value: DocumentType.CUSTOMER_SPECIFIC, label: "Tài liệu khách hàng" },
  { value: DocumentType.COMMON_GUIDE,      label: "Hướng dẫn chung" },
]

const STAGE_LABEL: Record<string, string> = {
  idle:       "",
  signing:    "Đang tạo Signed URL…",
  uploading:  "Đang upload lên Google Cloud Storage…",
  confirming: "Đang lưu thông tin tài liệu…",
}

export function UploadForm() {
  const router      = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [file,    setFile]    = useState<File | null>(null)
  const [docType, setDocType] = useState<DocumentType>(DocumentType.COMMON_GUIDE)
  const [groupId, setGroupId] = useState("")
  const [dragging, setDragging] = useState(false)

  const { mutateAsync, isPending, progress, stage } = useUploadDocument()

  const handleFile = (f: File) => {
    if (!isPdf(f.name) && !isDocx(f.name)) {
      toast.error("Chỉ chấp nhận file PDF hoặc DOCX")
      return
    }
    setFile(f)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) handleFile(dropped)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) { toast.error("Vui lòng chọn file"); return }
    const doc = await mutateAsync({
      file,
      document_type:     docType,
      document_group_id: groupId.trim() || undefined,
    })
    toast.success("Upload lên Google Cloud Storage thành công!")
    router.push(`/documents/${doc.id}`)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-lg">
      {/* Drop zone */ /*}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative flex flex-col items-center justify-center gap-2 p-10 border-2 border-dashed
                    rounded-xl cursor-pointer transition-colors select-none
                    ${dragging ? "border-blue-500 bg-blue-50" : "border-slate-300 hover:border-blue-400"}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
        <span className="text-3xl">{file ? (isPdf(file.name) ? "📄" : "📝") : "☁️"}</span>
        {file ? (
          <div className="text-center">
            <p className="text-sm font-medium text-blue-700">{file.name}</p>
            <p className="text-xs text-slate-400 mt-0.5">{formatFileSize(file.size)}</p>
          </div>
        ) : (
          <>
            <p className="text-sm font-medium text-slate-700">
              Kéo thả hoặc nhấp để chọn file
            </p>
            <p className="text-xs text-slate-400">PDF, DOCX — tối đa 100MB</p>
            <p className="text-xs text-slate-400 mt-1">
              File sẽ được upload trực tiếp lên{" "}
              <span className="text-blue-500">Google Cloud Storage</span>
            </p>
          </>
        )}
      </div>

      {/* Document type */ /*}
      <div className="space-y-1">
        <label className="text-sm font-medium text-slate-700">Loại tài liệu</label>
        <select
          value={docType}
          onChange={(e) => setDocType(e.target.value as DocumentType)}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm
                     focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
        >
          {TYPE_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {/* Group ID for versioning */ /*}
      <div className="space-y-1">
        <label className="text-sm font-medium text-slate-700">
          Group ID{" "}
          <span className="font-normal text-slate-400">(để trống nếu là tài liệu mới)</span>
        </label>
        <input
          type="text"
          value={groupId}
          onChange={(e) => setGroupId(e.target.value)}
          placeholder="uuid của document_group_id hiện có…"
          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-mono
                     focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Upload progress */ /*}
      {isPending && (
        <div className="space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-600 font-medium">{STAGE_LABEL[stage]}</span>
            {stage === "uploading" && (
              <span className="text-blue-600 font-semibold">{progress}%</span>
            )}
          </div>

          {/* Step indicator */ /*}
          <div className="flex items-center gap-2">
            {(["signing", "uploading", "confirming"] as const).map((s, i) => (
              <div key={s} className="flex items-center gap-1 flex-1">
                <div
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold transition-colors
                    ${stage === s ? "bg-blue-600 text-white" :
                      ["signing", "uploading", "confirming"].indexOf(stage) > i
                        ? "bg-emerald-500 text-white"
                        : "bg-slate-200 text-slate-400"
                    }`}
                >
                  {["signing", "uploading", "confirming"].indexOf(stage) > i ? "✓" : i + 1}
                </div>
                {i < 2 && <div className={`flex-1 h-0.5 ${["signing", "uploading", "confirming"].indexOf(stage) > i ? "bg-emerald-500" : "bg-slate-200"}`} />}
              </div>
            ))}
          </div>

          {/* Progress bar for GCS upload */ /*}
          {stage === "uploading" && (
            <div className="w-full bg-slate-200 rounded-full h-1.5">
              <div
                className="bg-blue-600 h-1.5 rounded-full transition-all duration-200"
                style={{ width: `${progress}%` }}
              />
            </div>
          )}
        </div>
      )}

      <button
        type="submit"
        disabled={isPending || !file}
        className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-60
                   text-white text-sm font-semibold rounded-lg transition-colors"
      >
        {isPending ? "Đang xử lý…" : "☁️ Upload lên Cloud Storage"}
      </button>
    </form>
  )
}
*/

interface UploadFormProps {
  onClose: () => void;
}

export default function UploadForm({ onClose }: UploadFormProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  // State cho Metadata
  const [docName, setDocName] = useState("");
  const [docType, setDocType] = useState("report");
  const [description, setDescription] = useState("");

  // Xử lý khi chọn file
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setDocName(file.name.replace(/\.[^/.]+$/, "")); // Tự động lấy tên file làm tên tài liệu

      // Giả lập tiến trình tải lên từ Frontend (UI)
      setUploadProgress(0);
      const interval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 10;
        });
      }, 200);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setUploadProgress(0);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    // TODO: Tích hợp gọi Backend API tại đây
    // 1. Tạo FormData chứa file và metadata
    // const formData = new FormData();
    // formData.append('file', selectedFile);
    // formData.append('name', docName);
    // formData.append('type', docType);
    // formData.append('description', description);

    // 2. Dùng axios POST lên backend: axios.post('/api/documents/upload', formData)
    // 3. Backend nhận file stream và bắn thẳng lên Google Cloud Storage (GCS).

    console.log("Đang upload...", {
      file: selectedFile.name,
      docName,
      docType,
    });

    // Đóng form sau khi thành công
    // onClose();
  };

  return (
    <div className="absolute inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-on-background/20 backdrop-blur-sm transition-opacity duration-300">
      <div className="bg-surface-container-lowest w-full max-w-lg rounded-[1rem] shadow-[0_10px_40px_-10px_rgba(43,52,55,0.15)] flex flex-col overflow-hidden max-h-[600px]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-surface-variant/40 flex justify-between items-center bg-surface-container-lowest shrink-0">
          <h2 className="font-headline text-xl font-bold tracking-tight text-on-background">
            Tải lên tài liệu
          </h2>
          <button
            onClick={onClose}
            className="text-on-surface-variant hover:text-on-background hover:bg-surface-container p-1.5 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-tertiary/30"
          >
            <span
              className="material-symbols-outlined"
              style={{ fontSize: "20px" }}
            >
              close
            </span>
          </button>
        </div>

        {/* Form Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Drag & Drop Zone */}
          {!selectedFile && (
            <div className="border-2 border-dashed border-outline-variant/60 rounded-xl bg-surface-container-low/50 hover:bg-surface-container-low hover:border-tertiary/50 transition-all duration-200 group flex flex-col items-center justify-center py-10 px-4 text-center cursor-pointer relative overflow-hidden">
              <div className="w-14 h-14 rounded-full bg-secondary-container/50 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                <span
                  className="material-symbols-outlined text-secondary text-3xl"
                  style={{ fontVariationSettings: '"FILL" 0' }}
                >
                  cloud_upload
                </span>
              </div>
              <h3 className="font-body font-medium text-on-background mb-1 text-base">
                Kéo và thả file của bạn vào đây
              </h3>
              <p className="font-body text-sm text-on-surface-variant mb-4">
                Hỗ trợ các định dạng .pdf, .doc, .docx lên đến 50MB
              </p>
              <button className="bg-surface-container-lowest border border-outline-variant/50 text-on-background px-4 py-2 rounded-lg font-medium text-sm hover:bg-surface transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-tertiary/30">
                Chọn file từ máy tính
              </button>
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                className="absolute inset-0 opacity-0 cursor-pointer"
                onChange={handleFileChange}
              />
            </div>
          )}

          {/* Uploading List (Chỉ hiện khi đã chọn file) */}
          {selectedFile && (
            <div className="space-y-3">
              <h4 className="font-body text-sm font-semibold tracking-wide text-on-background uppercase letter-spacing-[0.05em] mb-2 flex items-center gap-2">
                Đang tải lên{" "}
                <span className="bg-surface-container px-2 py-0.5 rounded-full text-xs font-medium text-on-surface-variant">
                  1
                </span>
              </h4>
              <div className="bg-surface-container-lowest border border-surface-variant/50 rounded-lg p-4 flex items-center gap-4 relative overflow-hidden group hover:border-outline-variant/50 transition-colors">
                {/* Progress Background fill */}
                <div
                  className="absolute left-0 top-0 bottom-0 bg-tertiary/5 z-0 transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>

                <div className="w-10 h-10 rounded bg-tertiary-container/20 flex items-center justify-center shrink-0 z-10 text-tertiary">
                  <span
                    className="material-symbols-outlined"
                    style={{ fontVariationSettings: '"FILL" 1' }}
                  >
                    picture_as_pdf
                  </span>
                </div>

                <div className="flex-1 min-w-0 z-10">
                  <div className="flex justify-between items-start mb-1">
                    <p className="font-body text-sm font-medium text-on-background truncate pr-4">
                      {selectedFile.name}
                    </p>
                    <span className="font-body text-xs text-on-surface-variant whitespace-nowrap">
                      {uploadProgress}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <p className="font-body text-xs text-on-surface-variant">
                      {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                    <button
                      onClick={handleRemoveFile}
                      className="text-on-surface-variant hover:text-error opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-md hover:bg-error-container/20"
                    >
                      <span
                        className="material-symbols-outlined"
                        style={{ fontSize: "16px" }}
                      >
                        close
                      </span>
                    </button>
                  </div>
                </div>
                {/* Progress line at bottom */}
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-surface-container z-0">
                  <div
                    className="h-full bg-tertiary rounded-r-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </div>
            </div>
          )}

          <hr className="border-surface-variant/50 border-t my-6" />

          {/* Metadata Form */}
          <div className="space-y-4">
            <h4 className="font-headline text-lg font-semibold text-on-background mb-4">
              Thông tin chi tiết
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5 md:col-span-2">
                <label className="font-label text-sm font-medium text-on-surface block">
                  Tên tài liệu <span className="text-error">*</span>
                </label>
                <input
                  type="text"
                  value={docName}
                  onChange={(e) => setDocName(e.target.value)}
                  className="w-full bg-surface-container-lowest border-none ring-1 ring-inset ring-outline-variant/40 focus:ring-2 focus:ring-inset focus:ring-tertiary rounded-lg px-3 py-2.5 font-body text-sm text-on-background shadow-sm placeholder:text-on-surface-variant transition-all"
                />
              </div>
              <div className="space-y-1.5 md:col-span-2">
                <label className="font-label text-sm font-medium text-on-surface block">
                  Loại tài liệu
                </label>
                <div className="relative">
                  <select
                    value={docType}
                    onChange={(e) => setDocType(e.target.value)}
                    className="w-full bg-surface-container-lowest border-none ring-1 ring-inset ring-outline-variant/40 focus:ring-2 focus:ring-inset focus:ring-tertiary rounded-lg px-3 py-2.5 font-body text-sm text-on-background shadow-sm appearance-none cursor-pointer pr-10 transition-all"
                  >
                    <option disabled value="">
                      Chọn phân loại
                    </option>
                    <option value="report">Báo cáo (Report)</option>
                    <option value="blueprint">Bản vẽ (Blueprint)</option>
                    <option value="contract">Hợp đồng (Contract)</option>
                    <option value="other">Khác</option>
                  </select>
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-on-surface-variant">
                    <span
                      className="material-symbols-outlined"
                      style={{ fontSize: "20px" }}
                    >
                      expand_more
                    </span>
                  </div>
                </div>
              </div>
              <div className="space-y-1.5 md:col-span-2">
                <label className="font-label text-sm font-medium text-on-surface block">
                  Mô tả thêm{" "}
                  <span className="text-on-surface-variant font-normal">
                    (Tùy chọn)
                  </span>
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-surface-container-lowest border-none ring-1 ring-inset ring-outline-variant/40 focus:ring-2 focus:ring-inset focus:ring-tertiary rounded-lg px-3 py-2.5 font-body text-sm text-on-background shadow-sm placeholder:text-on-surface-variant transition-all resize-none"
                  placeholder="Nhập tóm tắt nội dung hoặc ghi chú cho tài liệu này..."
                  rows={3}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 bg-surface-container-low/30 border-t border-surface-variant/40 flex justify-end gap-3 shrink-0">
          <button
            onClick={onClose}
            className="px-5 py-2.5 rounded-lg font-label font-medium text-sm text-on-surface hover:bg-surface-container transition-colors focus:outline-none focus:ring-2 focus:ring-outline-variant"
          >
            Hủy
          </button>
          <button
            onClick={handleSubmit}
            disabled={!selectedFile || uploadProgress < 100}
            className="px-5 py-2.5 rounded-lg font-label font-medium text-sm text-on-primary shadow-sm flex items-center gap-2 transition-all focus:outline-none focus:ring-2 focus:ring-tertiary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              background: "linear-gradient(180deg, #0053dc 0%, #0049c2 100%)",
            }}
          >
            <span
              className="material-symbols-outlined"
              style={{ fontSize: "18px" }}
            >
              cloud_upload
            </span>
            Tải lên
          </button>
        </div>
      </div>
    </div>
  );
}
