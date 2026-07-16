"use client";

import type { Status } from "@/types/document";

const STATUS_CLASSES: Record<Status, string> = {
  draft: "bg-gray-100 text-gray-700",
  pending_review: "bg-yellow-100 text-yellow-800",
  approved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-700",
  expired: "bg-orange-100 text-orange-700",
  active: "bg-blue-100 text-blue-800",
  archived: "bg-slate-200 text-slate-500",
};

const STATUS_LABELS: Record<Status, string> = {
  draft: "Draft",
  pending_review: "Pending Review",
  approved: "Approved",
  rejected: "Rejected",
  expired: "Expired",
  active: "Active",
  archived: "Archived",
};

export function StatusBadge({ status }: { status: Status | string }) {
  const s = String(status).toLowerCase() as Status;
  const cls = STATUS_CLASSES[s] ?? "bg-gray-100 text-gray-700";
  const label = STATUS_LABELS[s] ?? status;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${cls}`}
    >
      {label}
    </span>
  );
}

export { STATUS_LABELS };
