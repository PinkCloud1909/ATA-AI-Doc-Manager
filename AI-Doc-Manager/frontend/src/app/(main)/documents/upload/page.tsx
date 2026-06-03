import UploadForm from "@/components/documents/UploadForm";

export default function UploadPage() {
  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Upload tài liệu</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Tải lên tài liệu mới hoặc phiên bản mới của tài liệu hiện có
        </p>
      </div>
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        {/* <UploadForm /> */}
      </div>
    </div>
  );
}
