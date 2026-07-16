"use client";

import React from "react";
import Link from "next/link";
import { useDocumentList } from "@/hooks/useDocuments";

type ActivityType = "approval" | "upload" | "comment" | "edit";

interface Activity {
  id: string;
  user: string;
  action: string;
  time: string;
  details: string | React.ReactNode;
  type: ActivityType;
  badges?: { label: string; bgClass: string; textClass: string }[];
  targetLink?: string;
}

interface ActivityGroup {
  dateLabel: string;
  items: Activity[];
}

function formatTimeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return "Vừa xong";
  if (diffMins < 60) return `${diffMins} phút trước`;
  const diffHrs = Math.floor(diffMins / 60);
  if (diffHrs < 24) return `${diffHrs} giờ trước`;
  const diffDays = Math.floor(diffHrs / 24);
  return `${diffDays} ngày trước`;
}

function isToday(date: Date): boolean {
  const now = new Date();
  return date.toDateString() === now.toDateString();
}

function isYesterday(date: Date): boolean {
  const now = new Date();
  const yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);
  return date.toDateString() === yesterday.toDateString();
}

function buildActivitiesFromDocs(docs: any[]): ActivityGroup[] {
  const now = new Date();
  const todayItems: Activity[] = [];
  const yesterdayItems: Activity[] = [];
  const olderItems: Activity[] = [];

  docs.slice(0, 10).forEach((doc) => {
    const date = new Date(doc.modified_date ?? doc.created_at);
    const status = doc.status;
    const isApproved = status === "approved";
    const isSubmitted = status === "pending_review";

    const activity: Activity = {
      id: doc.document_id ?? doc.id,
      user: doc.created_by_name ?? doc.created_by ?? "Người dùng",
      action: isApproved ? "đã phê duyệt tài liệu" : isSubmitted ? "đã gửi phê duyệt" : "đã cập nhật tài liệu",
      time: formatTimeAgo(doc.modified_date ?? doc.created_at),
      details: doc.title ?? doc.original_filename ?? "Tài liệu",
      type: isApproved ? "approval" : isSubmitted ? "comment" : "edit",
      badges: [
        {
          label: doc.document_type ?? "Document",
          bgClass: "bg-surface-container",
          textClass: "text-on-surface-variant",
        },
        {
          label: status?.toUpperCase() ?? "DRAFT",
          bgClass: isApproved ? "bg-[#e6f4ea]" : isSubmitted ? "bg-[#fef7e0]" : "bg-tertiary-container",
          textClass: isApproved ? "text-[#1e4620]" : isSubmitted ? "text-[#b06000]" : "text-on-tertiary",
        },
      ],
      targetLink: `/documents/${doc.document_id ?? doc.id}`,
    };

    if (isToday(date)) {
      todayItems.push(activity);
    } else if (isYesterday(date)) {
      yesterdayItems.push(activity);
    } else {
      olderItems.push(activity);
    }
  });

  const groups: ActivityGroup[] = [];
  if (todayItems.length > 0) groups.push({ dateLabel: "Hôm nay", items: todayItems });
  if (yesterdayItems.length > 0) groups.push({ dateLabel: "Hôm qua", items: yesterdayItems });
  if (olderItems.length > 0) {
    groups.push({ dateLabel: "Trước đó", items: olderItems });
  }

  return groups;
}

const getActivityIcon = (type: ActivityType) => {
  switch (type) {
    case "approval": return { icon: "check_circle", color: "text-tertiary" };
    case "upload": return { icon: "upload_file", color: "text-on-surface" };
    case "comment": return { icon: "chat_bubble", color: "text-secondary" };
    case "edit": return { icon: "edit_document", color: "text-on-surface" };
    default: return { icon: "notifications", color: "text-on-surface-variant" };
  }
};

export default function ActivityFeed() {
  const { data, isLoading } = useDocumentList({ page_size: 20 });
  const groups: ActivityGroup[] = data?.items ? buildActivitiesFromDocs(data.items) : [];

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <div className="w-8 h-8 border-3 border-tertiary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (groups.length === 0) {
    return (
      <div className="text-center py-12">
        <span className="material-symbols-outlined text-4xl text-on-surface-variant mb-2" style={{ fontSize: "40px" }}>
          history
        </span>
        <p className="text-sm text-on-surface-variant">
          Chưa có hoạt động nào. Tải lên tài liệu đầu tiên để bắt đầu.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {groups.map((group, groupIndex) => (
        <React.Fragment key={groupIndex}>
          <div
            className={`flex items-center space-x-4 mb-6 ${groupIndex === 0 ? "mt-8" : "mt-10"}`}
          >
            <span className="font-headline font-bold text-xs uppercase tracking-widest text-on-surface-variant">
              {group.dateLabel}
            </span>
            <div className="flex-1 h-px bg-surface-variant/50"></div>
          </div>

          {group.items.map((activity) => {
            const { icon, color } = getActivityIcon(activity.type);
            return (
              <div
                key={activity.id}
                className="bg-surface-container-lowest rounded-xl p-5 hover:bg-surface-container-low transition-colors duration-200 group flex items-start space-x-4"
              >
                <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center shrink-0">
                  <span className={`material-symbols-outlined ${color}`}>{icon}</span>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start mb-1">
                    <p className="text-sm font-medium text-on-surface truncate">
                      <span className="font-semibold">{activity.user}</span>{" "}
                      {activity.action}
                    </p>
                    <span className="text-xs text-on-surface-variant whitespace-nowrap ml-4">
                      {activity.time}
                    </span>
                  </div>

                  {typeof activity.details === "string" ? (
                    activity.targetLink ? (
                      <Link
                        href={activity.targetLink}
                        className="text-sm text-on-surface-variant line-clamp-2 mt-1 hover:text-tertiary hover:underline block"
                      >
                        {activity.details}
                      </Link>
                    ) : (
                      <p className="text-sm text-on-surface-variant line-clamp-2 mt-1">
                        {activity.details}
                      </p>
                    )
                  ) : (
                    <div className="text-sm text-on-surface-variant mt-2">{activity.details}</div>
                  )}

                  {activity.badges && activity.badges.length > 0 && (
                    <div className="mt-3 flex items-center space-x-3">
                      {activity.badges.map((badge, idx) => (
                        <span
                          key={idx}
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${badge.bgClass} ${badge.textClass}`}
                        >
                          {badge.label}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </React.Fragment>
      ))}
    </div>
  );
}
