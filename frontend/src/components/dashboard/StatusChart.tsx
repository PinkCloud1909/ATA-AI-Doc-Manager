"use client";

import React from "react";
import { useDocumentList } from "@/hooks/useDocuments";
import { useTranslation } from "@/i18n/LanguageContext";

export default function StatusChart() {
  const { t } = useTranslation();

  const { data: approvedData } = useDocumentList({ status_filter: "approved", page_size: 1 });
  const { data: pendingData } = useDocumentList({ status_filter: "pending_review", page_size: 1 });
  const { data: draftData } = useDocumentList({ status_filter: "draft", page_size: 1 });
  const { data: rejectedData } = useDocumentList({ status_filter: "rejected", page_size: 1 });
  const { data: expiredData } = useDocumentList({ status_filter: "expired", page_size: 1 });

  const bars = [
    { label: t.status.draft, count: draftData?.total ?? 0, color: "bg-slate-400" },
    { label: t.status.pending_review, count: pendingData?.total ?? 0, color: "bg-amber-500" },
    { label: t.status.approved, count: approvedData?.total ?? 0, color: "bg-tertiary" },
    { label: t.status.rejected, count: rejectedData?.total ?? 0, color: "bg-red-500" },
    { label: t.status.expired, count: expiredData?.total ?? 0, color: "bg-purple-500" },
  ];

  const maxCount = Math.max(...bars.map((b) => b.count), 1);

  return (
    <div className="w-full bg-surface-container-lowest p-6 lg:p-8 rounded-xl border border-outline-variant/15 shadow-sm">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-lg font-bold text-on-surface">{t.dashboard.statusDistribution}</h2>
          <p className="text-xs text-on-surface-variant mt-1">
            {t.dashboard.statusDistributionDesc}
          </p>
        </div>
      </div>

      <div className="h-64 flex items-end gap-3 md:gap-6 px-2 lg:px-8">
        {bars.map((bar) => {
          const heightPct = maxCount > 0 ? (bar.count / maxCount) * 100 : 0;
          return (
            <div key={bar.label} className="flex-1 flex flex-col items-center gap-2 h-full justify-end max-w-[120px]">
              <span className="text-sm font-bold text-on-surface">{bar.count}</span>
              <div className="w-full bg-surface-container-low rounded-t-lg flex-1 flex flex-col justify-end">
                <div
                  className={`w-full ${bar.color} rounded-t-lg transition-all duration-500`}
                  style={{ height: `${Math.max(heightPct, 4)}%` }}
                />
              </div>
              <span className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">
                {bar.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
