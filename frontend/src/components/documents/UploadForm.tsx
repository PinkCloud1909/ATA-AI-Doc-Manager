"use client";

import { useState, type ChangeEvent, type FormEvent } from "react";
import { useUploadDocument } from "@/hooks/useDocuments";
import { toast } from "sonner";
import { useTranslation } from "@/i18n/LanguageContext";
import type { DocumentType } from "@/types/document";

const MAX_UPLOAD_SIZE_BYTES = 100 * 1024 * 1024; // 100MB

const DOC_TYPE_OPTIONS: { value: DocumentType; labelKey: string }[] = [
  { value: "policy", labelKey: "policy" },
  { value: "manual", labelKey: "manual" },
  { value: "report", labelKey: "report" },
  { value: "other", labelKey: "other" },
];

function getErrorMessage(err: unknown): string {
  if (err && typeof err === "object" && "response" in err) {
    const resp = (err as { response?: { data?: { detail?: unknown } } }).response;
    const detail = resp?.data?.detail;
    if (typeof detail === "string") return detail;
  }
  return err instanceof Error ? err.message : "Upload failed";
}

interface UploadFormProps {
  onClose: () => void;
}

export default function UploadForm({ onClose }: UploadFormProps) {
  const { t } = useTranslation();
  const upload = useUploadDocument();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [docName, setDocName] = useState("");
  const [docType, setDocType] = useState<DocumentType>("other");
  const [description, setDescription] = useState("");

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      const file = e.target.files[0];
      if (file.size > MAX_UPLOAD_SIZE_BYTES) {
        toast.error("File exceeds 100MB limit");
        return;
      }
      setSelectedFile(file);
      setDocName(file.name.replace(/\.[^/.]+$/, ""));
    }
  };

  const handleRemoveFile = () => {
    if (!upload.isPending) {
      setSelectedFile(null);
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedFile) return;

    try {
      await upload.mutateAsync({
        file: selectedFile,
        documentType: docType,
        title: docName.trim() || undefined,
        description: description.trim() || undefined,
      });
      toast.success("Document uploaded successfully");
      onClose();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <form
        onSubmit={handleSubmit}
        className="bg-surface-container-lowest w-full max-w-lg rounded-xl shadow-xl flex flex-col max-h-[90vh]"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b flex justify-between items-center shrink-0">
          <h2 className="font-bold text-lg">{t.documents.uploadTitle}</h2>
          <button
            type="button"
            onClick={onClose}
            disabled={upload.isPending}
            className="p-1.5 rounded-full hover:bg-surface-container transition-colors disabled:opacity-50"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {!selectedFile ? (
            <div className="border-2 border-dashed border-outline-variant/60 rounded-xl bg-surface-container-low/50 p-10 text-center relative">
              <div className="w-14 h-14 rounded-full bg-secondary-container/50 flex items-center justify-center mx-auto mb-4">
                <span className="material-symbols-outlined text-secondary text-3xl">cloud_upload</span>
              </div>
              <h3 className="font-medium mb-1">{t.documents.dragDrop}</h3>
              <p className="text-sm text-on-surface-variant mb-4">{t.documents.supportedFormats}</p>
              <button
                type="button"
                className="px-4 py-2 bg-surface-container-lowest border rounded-lg text-sm font-medium"
              >
                {t.documents.chooseFile}
              </button>
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                className="absolute inset-0 opacity-0 cursor-pointer"
                onChange={handleFileChange}
              />
            </div>
          ) : (
            <div className="space-y-3">
              <div className="bg-surface-container-lowest border rounded-lg p-4 flex items-center gap-4">
                <div className="w-10 h-10 rounded bg-tertiary-container/20 flex items-center justify-center shrink-0 text-tertiary">
                  <span className="material-symbols-outlined">picture_as_pdf</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{selectedFile.name}</p>
                  <p className="text-xs text-on-surface-variant">
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                    {upload.isPending && ` · ${upload.progress}%`}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleRemoveFile}
                  disabled={upload.isPending}
                  className="p-1 hover:text-error disabled:opacity-50"
                >
                  <span className="material-symbols-outlined text-[16px]">close</span>
                </button>
              </div>
              {upload.isPending && (
                <div className="w-full bg-surface-container rounded-full h-1.5">
                  <div
                    className="bg-tertiary h-1.5 rounded-full transition-all duration-300"
                    style={{ width: `${upload.progress}%` }}
                  />
                </div>
              )}
            </div>
          )}

          <hr className="border-surface-variant/50" />

          <div className="space-y-4">
            <h4 className="font-semibold">{t.documents.details}</h4>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">
                {t.documents.documentName} <span className="text-error">*</span>
              </label>
              <input
                type="text"
                value={docName}
                onChange={(e) => setDocName(e.target.value)}
                className="w-full bg-surface-container-lowest ring-1 ring-outline-variant/40 focus:ring-2 focus:ring-tertiary rounded-lg px-3 py-2.5 text-sm"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">{t.documents.documentType}</label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value as DocumentType)}
                className="w-full bg-surface-container-lowest ring-1 ring-outline-variant/40 focus:ring-2 focus:ring-tertiary rounded-lg px-3 py-2.5 text-sm"
              >
                {DOC_TYPE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {(t.documentType as Record<string, string>)[opt.labelKey] ?? opt.value}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">
                {t.documents.description}{" "}
                <span className="text-on-surface-variant font-normal">(Optional)</span>
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-surface-container-lowest ring-1 ring-outline-variant/40 focus:ring-2 focus:ring-tertiary rounded-lg px-3 py-2.5 text-sm resize-none"
                rows={3}
                placeholder="Enter a brief description..."
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t flex justify-end gap-3 shrink-0">
          <button
            type="button"
            onClick={onClose}
            disabled={upload.isPending}
            className="px-5 py-2.5 rounded-lg text-sm text-on-surface hover:bg-surface-container transition-colors disabled:opacity-50"
          >
            {t.common.cancel}
          </button>
          <button
            type="submit"
            disabled={!selectedFile || upload.isPending}
            className="px-5 py-2.5 rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-[18px]">cloud_upload</span>
            {upload.isPending ? "Uploading..." : t.documents.uploadButton}
          </button>
        </div>
      </form>
    </div>
  );
}
