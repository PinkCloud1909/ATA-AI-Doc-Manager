"use client";

import React from "react";
import { useDocumentList } from "@/hooks/useDocuments";

export default function DocumentStats() {
  const { data: allDocs } = useDocumentList({ page_size: 1 });
  const { data: approvedDocs } = useDocumentList({ status_filter: "approved", page_size: 1 });

  const totalDocs = allDocs?.total ?? 0;
  const approvedCount = approvedDocs?.total ?? 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="bg-blue-50/50 p-6 rounded-2xl border border-blue-100 flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center text-blue-600">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: '"FILL" 1' }}>
            analytics
          </span>
        </div>
        <div>
          <h4 className="text-sm font-bold text-blue-900">Tổng tài liệu</h4>
          <p className="text-2xl font-black text-blue-700">{totalDocs}</p>
        </div>
      </div>
      <div className="bg-green-50/50 p-6 rounded-2xl border border-green-100 flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center text-green-600">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: '"FILL" 1' }}>
            task_alt
          </span>
        </div>
        <div>
          <h4 className="text-sm font-bold text-green-900">Đã phê duyệt</h4>
          <p className="text-2xl font-black text-green-700">
            {approvedCount}{" "}
            <span className="text-xs font-medium text-green-600/70">tài liệu</span>
          </p>
        </div>
      </div>
      <div className="bg-surface-container-low p-6 rounded-2xl border border-transparent flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-surface-container-high flex items-center justify-center text-on-surface-variant">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: '"FILL" 1' }}>
            inventory_2
          </span>
        </div>
        <div>
          <h4 className="text-sm font-bold text-on-surface">Tổng số</h4>
          <p className="text-2xl font-black text-on-surface">
            {totalDocs}{" "}
            <span className="text-xs font-medium text-on-surface-variant/70">tài liệu</span>
          </p>
        </div>
      </div>
    </div>
  );
}
