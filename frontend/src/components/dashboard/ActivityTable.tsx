"use client";

import React from "react";
import Link from "next/link";
import { useDocumentList } from "@/hooks/useDocuments";
import { useTranslation, formatT } from "@/i18n/LanguageContext";

interface ActivityItem {
  id: string;
  user: string;
  action: string;
  target: string;
  timestamp: string;
  details?: string;
  type: "update" | "approve" | "comment";
}

export default function ActivityTable() {
  const { t } = useTranslation();

  function formatTimeAgo(dateStr: string): string {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return t.activity.justNow;
    if (diffMins < 60) return formatT(t.activity.minutesAgo, { count: diffMins });
    const diffHrs = Math.floor(diffMins / 60);
    if (diffHrs < 24) return formatT(t.activity.hoursAgo, { count: diffHrs });
    const diffDays = Math.floor(diffHrs / 24);
    return formatT(t.activity.daysAgo, { count: diffDays });
  }

  function buildActivitiesFromDocs(docs: any[]): ActivityItem[] {
    return docs.slice(0, 5).map((doc) => {
      const status = doc.status;
      const isApproved = status === "approved";
      const isSubmitted = status === "pending_review";

      return {
        id: doc.document_id ?? doc.id,
        user: doc.created_by_name ?? doc.created_by ?? "User",
        action: isApproved ? t.activity.approved : isSubmitted ? t.activity.submittedForReview : t.activity.updated,
        target: doc.title ?? doc.original_filename ?? "Document",
        timestamp: formatTimeAgo(doc.modified_date ?? doc.created_at),
        details: doc.description?.slice(0, 100),
        type: isApproved ? "approve" : isSubmitted ? "comment" : "update",
      } as ActivityItem;
    });
  }

  const { data, isLoading } = useDocumentList({ page_size: 10 });

  const activities: ActivityItem[] = data?.items
    ? buildActivitiesFromDocs(data.items)
    : [];

  const getActivityStyle = (type: ActivityItem["type"]) => {
    switch (type) {
      case "update":
        return { icon: "edit_note", iconColor: "text-tertiary", bgColor: "bg-tertiary-container/10" };
      case "approve":
        return { icon: "verified", iconColor: "text-on-secondary-container", bgColor: "bg-secondary-container" };
      case "comment":
        return { icon: "add_comment", iconColor: "text-primary-dim", bgColor: "bg-surface-container-high" };
      default:
        return { icon: "notifications", iconColor: "text-on-surface-variant", bgColor: "bg-surface-container" };
    }
  };

  return (
    <div className="xl:col-span-2 bg-surface-container-lowest p-6 rounded-xl">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-bold text-on-surface">{t.dashboard.recentActivity}</h2>
        <Link
          href="/dashboard/activities"
          className="text-tertiary text-xs font-bold hover:underline transition-all"
        >
          {t.dashboard.viewAll}
        </Link>
      </div>

      <div className="space-y-4">
        {isLoading ? (
          <div className="flex justify-center py-8">
            <div className="w-6 h-6 border-2 border-tertiary border-t-transparent rounded-full animate-spin" />
          </div>
        ) : activities.length === 0 ? (
          <p className="text-sm text-on-surface-variant italic text-center py-4">
            {t.dashboard.noActivity}
          </p>
        ) : (
          activities.map((activity) => {
            const style = getActivityStyle(activity.type);
            return (
              <div
                key={activity.id}
                className="flex items-start gap-4 p-3 hover:bg-surface-container-low rounded-lg transition-colors"
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${style.bgColor}`}>
                  <span className={`material-symbols-outlined text-[20px] ${style.iconColor}`}>{style.icon}</span>
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-start">
                    <p className="text-sm font-semibold text-on-surface">
                      {activity.user}{" "}
                      <span className="font-normal text-on-surface-variant">{activity.action}</span>{" "}
                      &ldquo;{activity.target}&rdquo;
                    </p>
                    <span className="text-[10px] text-on-surface-variant font-medium whitespace-nowrap ml-2 mt-0.5">
                      {activity.timestamp}
                    </span>
                  </div>
                  {activity.type === "approve" ? (
                    <div className="mt-1 flex gap-2">
                      <span className="bg-on-tertiary-fixed-variant text-[10px] px-2 py-0.5 rounded-full text-tertiary font-bold uppercase tracking-wider border border-tertiary/10">
                        {t.status.approved}
                      </span>
                    </div>
                  ) : activity.details ? (
                    <p className="text-xs text-on-surface-variant mt-1 line-clamp-1">{activity.details}</p>
                  ) : null}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
