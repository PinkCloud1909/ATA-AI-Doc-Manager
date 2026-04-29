import React from "react";

interface DocumentPreviewProps {
  title: string;
  description: string;
  content: React.ReactNode;
}

export default function DocumentPreview({
  title,
  description,
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
      </div>
    </section>
  );
}
