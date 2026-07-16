"use client";

import React, { useState } from "react";
import { usePermission } from "@/hooks/usePermission";
import { useDocumentList } from "@/hooks/useDocuments";
import { useTranslation, formatT } from "@/i18n/LanguageContext";
import type { Status } from "@/types/document";

interface StatusCount {
  label: string;
  value: number;
  color: string;
  status: Status;
}

function createPieSlices(
  data: { label: string; value: number; color: string }[],
) {
  let cumulativePercent = 0;
  const total = data.reduce((sum, item) => sum + item.value, 0);

  return data.map((slice) => {
    const percent = total > 0 ? slice.value / total : 0;
    const startAngle = cumulativePercent * 2 * Math.PI - Math.PI / 2;
    cumulativePercent += percent;
    const endAngle = cumulativePercent * 2 * Math.PI - Math.PI / 2;

    const cx = 100, cy = 100, r = 100;

    const startX = cx + r * Math.cos(startAngle);
    const startY = cy + r * Math.sin(startAngle);
    const endX = cx + r * Math.cos(endAngle);
    const endY = cy + r * Math.sin(endAngle);

    const largeArcFlag = percent > 0.5 ? 1 : 0;

    const pathData =
      percent >= 1
        ? ""
        : [
            `M ${cx} ${cy}`,
            `L ${startX} ${startY}`,
            `A ${r} ${r} 0 ${largeArcFlag} 1 ${endX} ${endY}`,
            "Z",
          ].join(" ");

    const midAngle = startAngle + (endAngle - startAngle) / 2;
    const textX = cx + r * 0.65 * Math.cos(midAngle);
    const textY = cy + r * 0.65 * Math.sin(midAngle);

    return { ...slice, pathData, textX, textY, percent, total };
  });
}

export default function SummaryCards() {
  const { t } = useTranslation();
  const perm = usePermission();

  const role = perm.canApprove
    ? "approver"
    : perm.canUpload
      ? "editor"
      : "viewer";

  const STATUS_CONFIG: StatusCount[] = [
    { label: t.status.approved, value: 0, color: "#0053dc", status: "approved" },
    { label: t.status.pending_review, value: 0, color: "#f59e0b", status: "pending_review" },
    { label: t.status.draft, value: 0, color: "#9ca3af", status: "draft" },
    { label: t.status.rejected, value: 0, color: "#ef4444", status: "rejected" },
    { label: t.status.expired, value: 0, color: "#8b5cf6", status: "expired" },
  ];

  const { data: allDocs } = useDocumentList({ page_size: 1 });
  const totalDocs = allDocs?.total ?? 0;

  const { data: approvedData } = useDocumentList({ status_filter: "approved", page_size: 1 });
  const { data: pendingData } = useDocumentList({ status_filter: "pending_review", page_size: 1 });
  const { data: draftData } = useDocumentList({ status_filter: "draft", page_size: 1 });
  const { data: rejectedData } = useDocumentList({ status_filter: "rejected", page_size: 1 });
  const { data: expiredData } = useDocumentList({ status_filter: "expired", page_size: 1 });

  const counts: Record<string, number> = {
    approved: approvedData?.total ?? 0,
    pending: pendingData?.total ?? 0,
    draft: draftData?.total ?? 0,
    rejected: rejectedData?.total ?? 0,
    expired: expiredData?.total ?? 0,
  };

  const statusCountMap: Record<string, string> = {
    approved: "approved",
    pending_review: "pending",
    draft: "draft",
    rejected: "rejected",
    expired: "expired",
  };

  const chartData =
    role === "viewer"
      ? [
          { label: t.status.approved, value: counts.approved, color: "#0053dc" },
          {
            label: "Other",
            value: counts.pending + counts.draft + counts.rejected + counts.expired,
            color: "#9ca3af",
          },
        ]
      : STATUS_CONFIG.map((s) => ({ ...s, value: counts[statusCountMap[s.status] ?? "draft"] ?? 0 }));

  const filteredData = chartData.filter((d) => d.value > 0);
  const slices = createPieSlices(filteredData);

  const [tooltip, setTooltip] = useState<{
    visible: boolean;
    x: number;
    y: number;
    label: string;
    value: number;
    percent: number;
  }>({ visible: false, x: 0, y: 0, label: "", value: 0, percent: 0 });

  const handleMouseMove = (e: React.MouseEvent, slice: any) => {
    setTooltip({
      visible: true,
      x: e.clientX,
      y: e.clientY,
      label: slice.label,
      value: slice.value,
      percent: slice.percent,
    });
  };

  const handleMouseLeave = () => setTooltip({ ...tooltip, visible: false });

  if (totalDocs === 0 && !allDocs) {
    return (
      <div className="bg-surface-container-lowest p-8 rounded-xl border border-outline-variant/15 text-center">
        <span className="material-symbols-outlined text-4xl text-on-surface-variant mb-2" style={{ fontSize: "40px" }}>
          inventory_2
        </span>
        <p className="text-sm text-on-surface-variant">{t.dashboard.noDocumentsYet}</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 relative">
      {tooltip.visible && (
        <div
          className="fixed z-50 bg-inverse-surface text-on-tertiary-fixed px-3 py-2 rounded-lg shadow-xl text-sm font-medium pointer-events-none transform -translate-x-1/2 -translate-y-full mt-[-10px]"
          style={{ left: tooltip.x, top: tooltip.y }}
        >
          <div className="flex flex-col items-center">
            <span className="font-bold opacity-80 uppercase tracking-widest text-[10px]">{tooltip.label}</span>
            <span>{tooltip.value} {t.dashboard.title.toLowerCase()}</span>
          </div>
          <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-inverse-surface"></div>
        </div>
      )}

      <div className="lg:col-span-2 bg-surface-container-lowest p-6 lg:p-8 rounded-xl border border-outline-variant/15 shadow-sm flex flex-col sm:flex-row items-center gap-10">
        <div className="relative w-48 h-48 shrink-0 drop-shadow-sm hover:drop-shadow-md transition-shadow">
          <svg
            viewBox="0 0 200 200"
            className="w-full h-full rounded-full transform hover:scale-105 transition-transform duration-300"
          >
            {slices.length === 0 ? (
              <circle cx="100" cy="100" r="100" fill="#e5e7eb" />
            ) : slices.length === 1 ? (
              <circle
                cx="100" cy="100" r="100"
                fill={slices[0].color}
                onMouseMove={(e) => handleMouseMove(e, slices[0])}
                onMouseLeave={handleMouseLeave}
              />
            ) : (
              slices.map((slice, index) => (
                <g key={index} className="hover:opacity-90 transition-opacity cursor-pointer">
                  <path
                    d={slice.pathData}
                    fill={slice.color}
                    stroke="#ffffff"
                    strokeWidth="1.5"
                    onMouseMove={(e) => handleMouseMove(e, slice)}
                    onMouseLeave={handleMouseLeave}
                  />
                  {slice.percent > 0.05 && (
                    <text
                      x={slice.textX} y={slice.textY}
                      fill="#ffffff" fontSize="14" fontWeight="bold"
                      fontFamily="Inter" textAnchor="middle" alignmentBaseline="middle"
                      className="pointer-events-none"
                    >
                      {Math.round(slice.percent * 100)}%
                    </text>
                  )}
                </g>
              ))
            )}
          </svg>
        </div>

        <div className="flex-1 w-full space-y-5">
          <div>
            <h3 className="text-xl font-bold text-on-surface tracking-tight">{t.dashboard.statusOverview}</h3>
            <p className="text-sm text-on-surface-variant mt-0.5">
              {formatT(t.dashboard.documentsInSystem.replace("{count}", String(totalDocs)), { count: totalDocs })}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {filteredData.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-surface-container-low transition-colors border border-transparent hover:border-outline-variant/10"
              >
                <div className="w-4 h-4 rounded-full shrink-0 shadow-sm" style={{ backgroundColor: item.color }}></div>
                <div>
                  <p className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">{item.label}</p>
                  <p className="text-lg font-extrabold text-on-surface">{item.value}</p>
                </div>
              </div>
            ))}
            {filteredData.length === 0 && (
              <p className="col-span-2 text-sm text-on-surface-variant">{t.common.noResults}</p>
            )}
          </div>
        </div>
      </div>

      {/* Pending items alert */}
      <div className="bg-surface-container-lowest p-6 lg:p-8 rounded-xl border border-outline-variant/15 shadow-sm flex flex-col justify-between group hover:border-error/30 transition-colors relative overflow-hidden">
        <div className="absolute -right-6 -top-6 w-32 h-32 bg-error/5 rounded-full blur-3xl group-hover:bg-error/10 transition-colors"></div>
        <div>
          <div className="w-12 h-12 rounded-full bg-error-container flex items-center justify-center text-error mb-5">
            <span className="material-symbols-outlined text-[24px]">priority_high</span>
          </div>
          <h3 className="text-lg font-bold text-on-surface mb-2">{t.dashboard.needsAttention}</h3>
          <p className="text-sm text-on-surface-variant leading-relaxed">
            {counts.pending > 0 ? (
              <>
                {formatT(t.dashboard.pendingReview, { count: counts.pending })}
              </>
            ) : (
              t.dashboard.noPending
            )}
          </p>
        </div>
        <a
          href="/approvals"
          className="w-full mt-6 py-3 rounded-lg bg-surface-container text-on-surface font-semibold text-sm hover:bg-surface-container-high transition-colors flex items-center justify-center gap-2"
        >
          {counts.pending > 0 ? t.dashboard.goToQueue : t.dashboard.viewAllDocuments}
          <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
        </a>
      </div>
    </div>
  );
}
