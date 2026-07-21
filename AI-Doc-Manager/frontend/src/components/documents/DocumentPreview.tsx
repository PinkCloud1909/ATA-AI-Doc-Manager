import React from "react";

interface DocumentPreviewProps {
  title: string;
  description: string;
<<<<<<< Updated upstream
  content: React.ReactNode;
=======
  previewUrl: string;
  downloadUrl: string;
  filename: string;
  contentType?: string | null;
  content?: React.ReactNode;
}

function getPreviewKind(contentType: string | null | undefined, filename: string) {
  const type = (contentType ?? "").toLowerCase();
  const extension = filename.toLowerCase().split(".").pop();
  if (type.startsWith("image/") || ["png", "jpg", "jpeg", "gif", "webp"].includes(extension ?? "")) return "image";
  if (type.includes("word") || type.includes("officedocument") || ["doc", "docx"].includes(extension ?? "")) return "office";
  if (type === "application/pdf" || extension === "pdf") return "iframe";
  if (type.startsWith("text/") || ["txt", "md", "csv"].includes(extension ?? "")) return "iframe";
  return "unsupported";
>>>>>>> Stashed changes
}

export default function DocumentPreview({
  title,
  description,
<<<<<<< Updated upstream
  content,
}: DocumentPreviewProps) {
  return (
    <section className="flex-1 bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/15 overflow-y-auto flex flex-col">
      <div className="p-8 max-w-4xl mx-auto w-full">
        {/* Tiêu đề & Mô tả tự động */}
        <div className="mb-8 border-b border-surface-container pb-6">
          <h1 className="text-3xl font-headline font-bold text-on-surface mb-4">
            {title}
          </h1>
          <p className="text-on-surface-variant text-sm leading-relaxed">
            {description}
          </p>
        </div>

        {/* Nội dung chi tiết tự động render */}
        <div className="prose prose-slate max-w-none font-body text-on-surface leading-loose space-y-6">
          {content}
        </div>
=======
  previewUrl,
  downloadUrl,
  filename,
  contentType,
  content,
}: DocumentPreviewProps) {
  const kind = getPreviewKind(contentType, filename);
  const viewerUrl = kind === "office"
    ? `https://docs.google.com/gview?embedded=1&url=${encodeURIComponent(previewUrl)}`
    : previewUrl;

  return (
    <section className="flex min-w-0 flex-1 flex-col overflow-hidden rounded-xl border border-outline-variant/15 bg-surface-container-lowest shadow-sm">
      <header className="border-b border-outline-variant/15 px-5 py-4 md:px-7">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="min-w-0">
            <h1 className="truncate font-headline text-2xl font-bold text-on-surface" title={title}>{title}</h1>
            <p className="mt-1 line-clamp-2 text-sm leading-relaxed text-on-surface-variant">{description}</p>
          </div>
          <a
            href={downloadUrl}
            download={filename}
            className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg bg-tertiary px-4 py-2.5 text-sm font-bold text-on-tertiary hover:bg-tertiary-dim"
          >
            <span className="material-symbols-outlined text-[18px]">download</span>
            Download
          </a>
        </div>
        {content && <div className="mt-4">{content}</div>}
      </header>

      <div className="relative flex min-h-[420px] flex-1 items-center justify-center overflow-auto bg-surface-container-low p-3">
        {kind === "image" && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={previewUrl} alt={title} className="max-h-full max-w-full object-contain" />
        )}
        {(kind === "iframe" || kind === "office") && (
          <iframe
            src={viewerUrl}
            title={`Preview: ${title}`}
            className="h-full min-h-[650px] w-full rounded bg-white"
            referrerPolicy="no-referrer"
          />
        )}
        {kind === "unsupported" && (
          <div className="max-w-md rounded-xl bg-white p-8 text-center shadow-sm">
            <span className="material-symbols-outlined text-5xl text-on-surface-variant">draft</span>
            <h2 className="mt-3 text-lg font-bold text-on-surface">Preview is not available for this file type</h2>
            <p className="mt-2 text-sm text-on-surface-variant">Download the original file to view its complete content and formatting.</p>
            <a href={downloadUrl} download={filename} className="mt-5 inline-flex items-center gap-2 rounded-lg bg-tertiary px-4 py-2.5 text-sm font-bold text-on-tertiary">
              <span className="material-symbols-outlined text-[18px]">download</span>
              Download {filename}
            </a>
          </div>
        )}
>>>>>>> Stashed changes
      </div>
    </section>
  );
}
