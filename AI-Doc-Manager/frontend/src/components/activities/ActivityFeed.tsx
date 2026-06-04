"use client";

import React from "react";
import Link from "next/link";

// 1. Định nghĩa kiểu dữ liệu cho Activity
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

// 2. Dữ liệu mock phân nhóm theo Ngày
const MOCK_ACTIVITY_GROUPS: ActivityGroup[] = [
  {
    dateLabel: "Hôm nay",
    items: [
      {
        id: "act-1",
        user: "Nguyễn Văn A",
        action: "đã phê duyệt tài liệu",
        time: "10 phút trước",
        details:
          '"Quy trình ISO 2024 - Bản sửa đổi lần 3" đã được duyệt và xuất bản lên Knowledge Base.',
        type: "approval",
        badges: [
          {
            label: "Document",
            bgClass: "bg-surface-container",
            textClass: "text-on-surface-variant",
          },
          {
            label: "APPROVED",
            bgClass: "bg-[#e6f4ea]",
            textClass: "text-[#1e4620]",
          },
        ],
      },
      {
        id: "act-2",
        user: "Trần Thị B",
        action: "đã tải lên tài liệu mới",
        time: "2 giờ trước",
        details: '"Báo cáo phân tích thị trường Q3/2023.pdf"',
        type: "upload",
        badges: [
          {
            label: "PDF",
            bgClass: "bg-surface-container",
            textClass: "text-on-surface-variant",
          },
          {
            label: "DRAFT",
            bgClass: "bg-tertiary-container",
            textClass: "text-on-tertiary",
          },
        ],
      },
    ],
  },
  {
    dateLabel: "Hôm qua",
    items: [
      {
        id: "act-3",
        user: "Lê Văn C",
        action: "đã để lại bình luận",
        time: "14:30",
        details: (
          <>
            <p className="italic border-l-2 border-surface-variant pl-3 line-clamp-2">
              "Cần cập nhật thêm số liệu dự phóng cho năm 2025 trong phần kết
              luận nhé."
            </p>
            <p className="text-xs text-on-surface-variant mt-2 not-italic">
              Trong tài liệu:{" "}
              <Link
                href="#"
                className="text-tertiary hover:underline font-medium"
              >
                Kế hoạch chiến lược 5 năm
              </Link>
            </p>
          </>
        ),
        type: "comment",
      },
      {
        id: "act-4",
        user: "Bạn",
        action: "đã chỉnh sửa Wiki",
        time: "09:15",
        details: 'Cập nhật trang "Hướng dẫn Onboarding nhân sự mới".',
        type: "edit",
      },
    ],
  },
];

// Hàm phụ trợ lấy Icon theo Type
const getActivityIcon = (type: ActivityType) => {
  switch (type) {
    case "approval":
      return { icon: "check_circle", color: "text-tertiary" };
    case "upload":
      return { icon: "upload_file", color: "text-on-surface" };
    case "comment":
      return { icon: "chat_bubble", color: "text-secondary" };
    case "edit":
      return { icon: "edit_document", color: "text-on-surface" };
    default:
      return { icon: "notifications", color: "text-on-surface-variant" };
  }
};

export default function ActivityFeed() {
  return (
    <div className="space-y-4">
      {MOCK_ACTIVITY_GROUPS.map((group, groupIndex) => (
        <React.Fragment key={groupIndex}>
          {/* Date Separator */}
          <div
            className={`flex items-center space-x-4 mb-6 ${groupIndex === 0 ? "mt-8" : "mt-10"}`}
          >
            <span className="font-headline font-bold text-xs uppercase tracking-widest text-on-surface-variant">
              {group.dateLabel}
            </span>
            <div className="flex-1 h-px bg-surface-variant/50"></div>
          </div>

          {/* Activity Items in Group */}
          {group.items.map((activity) => {
            const { icon, color } = getActivityIcon(activity.type);
            return (
              <div
                key={activity.id}
                className="bg-surface-container-lowest rounded-xl p-5 hover:bg-surface-container-low transition-colors duration-200 group flex items-start space-x-4"
              >
                {/* Icon */}
                <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center shrink-0">
                  <span className={`material-symbols-outlined ${color}`}>
                    {icon}
                  </span>
                </div>

                {/* Content */}
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
                    <p className="text-sm text-on-surface-variant line-clamp-2 mt-1">
                      {activity.details}
                    </p>
                  ) : (
                    <div className="text-sm text-on-surface-variant mt-2">
                      {activity.details}
                    </div>
                  )}

                  {/* Badges */}
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

      {/* Load More */}
      <div className="mt-12 text-center pb-12">
        <button className="text-sm font-medium text-tertiary hover:text-tertiary-dim transition-colors py-2 px-4 rounded-lg hover:bg-surface-container-low inline-flex items-center space-x-2">
          <span className="material-symbols-outlined text-[18px]">
            expand_more
          </span>
          <span>Tải thêm hoạt động</span>
        </button>
      </div>
    </div>
  );
}
