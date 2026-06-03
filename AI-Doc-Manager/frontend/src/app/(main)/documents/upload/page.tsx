import UploadForm from "@/components/documents/UploadForm"

export default function UploadPage() {
  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Upload tài liệu</h1>
        <p className="mt-0.5 text-sm text-slate-500">
          Tải lên tài liệu mới hoặc tạo phiên bản mới cho tài liệu hiện có.
        </p>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-6">
        <UploadForm />
      </div>
    </div>
  )
}
