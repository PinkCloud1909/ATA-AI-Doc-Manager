"use client";

import { useMemo, useState } from "react";

type NotificationCategory = "all" | "unread" | "system" | "document";

type NotificationItem = {
  id: string;
  title: string;
  description: string;
  time: string;
  icon: string;
  tone: "blue" | "gray" | "red" | "slate";
  category: Exclude<NotificationCategory, "all" | "unread">;
  unread?: boolean;
};

const notifications: NotificationItem[] = [
  {
    id: "doc-approved",
    title: 'Tài liệu "Quy trình ISO" đã được phê duyệt',
    description:
      'Bản nháp "Quy trình ISO 9001:2015" của bạn đã được Giám đốc chất lượng phê duyệt và chuyển sang trạng thái xuất bản.',
    time: "10 phút trước",
    icon: "description",
    tone: "blue",
    category: "document",
    unread: true,
  },
  {
    id: "comment",
    title: 'Bình luận mới trong "Kế hoạch Q3"',
    description:
      'Nguyễn Văn A: "Chúng ta cần xem xét lại ngân sách cho phần marketing online trong tháng tới..."',
    time: "1 giờ trước",
    icon: "forum",
    tone: "blue",
    category: "document",
    unread: true,
  },
  {
    id: "sync-error",
    title: "Lỗi đồng bộ dữ liệu",
    description:
      'Không thể đồng bộ thư mục "Tài liệu phòng Nhân sự" do lỗi kết nối mạng. Vui lòng kiểm tra lại đường truyền.',
    time: "Hôm qua, 14:30",
    icon: "error",
    tone: "red",
    category: "system",
    unread: true,
  },
  {
    id: "update",
    title: "Cập nhật hệ thống v2.4.1",
    description:
      "Hệ thống đã được nâng cấp với các tính năng tìm kiếm nâng cao và cải thiện hiệu suất tải trang.",
    time: "2 ngày trước",
    icon: "info",
    tone: "slate",
    category: "system",
  },
  {
    id: "member",
    title: "Thành viên mới tham gia dự án",
    description:
      'Trần Thị B đã được thêm vào không gian làm việc "Phát triển Sản phẩm 2024".',
    time: "3 ngày trước",
    icon: "group_add",
    tone: "gray",
    category: "system",
  },
];

const tabs: Array<{ key: NotificationCategory; label: string }> = [
  { key: "all", label: "Tất cả" },
  { key: "unread", label: "Chưa đọc" },
  { key: "system", label: "Hệ thống" },
  { key: "document", label: "Tài liệu" },
];

const toneClasses: Record<NotificationItem["tone"], string> = {
  blue: "bg-blue-50 text-tertiary",
  gray: "bg-surface-container text-on-surface-variant",
  red: "bg-red-50 text-error",
  slate: "bg-surface-container-low text-outline",
};

export default function NotificationsPage() {
  const [activeTab, setActiveTab] = useState<NotificationCategory>("all");
  const [items, setItems] = useState(notifications);

  const unreadCount = items.filter((item) => item.unread).length;

  const visibleItems = useMemo(() => {
    if (activeTab === "all") return items;
    if (activeTab === "unread") return items.filter((item) => item.unread);
    return items.filter((item) => item.category === activeTab);
  }, [activeTab, items]);

  const markAllAsRead = () => {
    setItems((current) => current.map((item) => ({ ...item, unread: false })));
  };

  return (
    <div className="mx-auto flex min-h-full w-full max-w-7xl flex-col px-4 py-6 md:px-8">
      <div className="mb-7 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-on-surface">
            Thông báo
          </h1>
          <p className="mt-2 text-sm text-on-surface-variant">
            Cập nhật hệ thống và hoạt động tài liệu.
          </p>
        </div>
        <button
          type="button"
          onClick={markAllAsRead}
          className="inline-flex items-center gap-1.5 self-start text-sm font-semibold text-tertiary transition-colors hover:text-tertiary-dim"
        >
          <span className="material-symbols-outlined text-[18px]">done_all</span>
          Đánh dấu tất cả là đã đọc
        </button>
      </div>

      <div className="border-b border-outline-variant/20">
        <div className="flex flex-wrap gap-7">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                type="button"
                onClick={() => setActiveTab(tab.key)}
                className={`relative flex h-10 items-center gap-2 text-sm font-semibold transition-colors ${
                  isActive
                    ? "text-tertiary"
                    : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                <span>{tab.label}</span>
                {tab.key === "unread" && unreadCount > 0 && (
                  <span className="min-w-6 rounded-full bg-surface-container px-2 py-0.5 text-center text-xs font-bold text-on-surface-variant">
                    {unreadCount}
                  </span>
                )}
                {isActive && (
                  <span className="absolute inset-x-0 -bottom-px h-0.5 rounded-full bg-tertiary" />
                )}
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-8 space-y-3">
        {visibleItems.map((item) => (
          <article
            key={item.id}
            className={`relative flex min-h-24 gap-5 border border-outline-variant/10 bg-white px-5 py-4 shadow-sm transition-colors hover:bg-surface-bright ${
              item.unread ? "border-l-4 border-l-tertiary" : ""
            }`}
          >
            <div
              className={`mt-1 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${toneClasses[item.tone]}`}
            >
              <span className="material-symbols-outlined text-[22px]">
                {item.icon}
              </span>
            </div>
            <div className="min-w-0 flex-1 pr-4">
              <h2 className="text-sm font-bold text-on-surface">{item.title}</h2>
              <p className="mt-1 line-clamp-2 text-sm leading-6 text-on-surface-variant">
                {item.description}
              </p>
            </div>
            <time className="shrink-0 pt-1 text-xs font-medium text-on-surface-variant">
              {item.time}
            </time>
          </article>
        ))}
      </div>

      <button
        type="button"
        className="mx-auto mt-9 inline-flex items-center gap-1.5 text-sm font-bold text-tertiary transition-colors hover:text-tertiary-dim"
      >
        Tải thêm
        <span className="material-symbols-outlined text-[18px]">expand_more</span>
      </button>
    </div>
  );
}
