"use client";

import React, { useState } from "react";

// Dữ liệu mock lịch sử chat
const MOCK_HISTORY = [
  {
    id: 1,
    title: "Quy trình ứng cứu sự cố hạ tầng v2",
    preview: "You: Hãy phân tích tài liệu...",
    group: "Today",
    active: true,
  },
  {
    id: 2,
    title: "Review IAM Policies",
    preview: "AI: Các thay đổi IAM được đề xuất...",
    group: "Today",
  },
  {
    id: 3,
    title: "Database Migration Runbook",
    preview: "AI: Đã tìm thấy 3 rủi ro tiềm ẩn...",
    group: "Yesterday",
  },
  {
    id: 4,
    title: "Weekly Network Status",
    preview: "You: Tóm tắt báo cáo mạng tuần trước...",
    group: "Yesterday",
  },
  {
    id: 5,
    title: "Kubernetes Cluster Upgrade",
    preview: "AI: Kế hoạch nâng cấp cluster...",
    group: "Last Week",
  },
  {
    id: 6,
    title: "Security Audit Response",
    preview: "You: Cần chuẩn bị gì cho đợt audit...",
    group: "Last Week",
  },
];

export default function ChatSidebar() {
  // State lưu từ khóa tìm kiếm
  const [searchQuery, setSearchQuery] = useState("");

  // Lọc dữ liệu theo từ khóa (không phân biệt hoa thường)
  const filteredHistory = MOCK_HISTORY.filter(
    (item) =>
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.preview.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  // Gom nhóm dữ liệu đã lọc theo trường 'group'
  const groupedHistory = filteredHistory.reduce(
    (acc, item) => {
      if (!acc[item.group]) acc[item.group] = [];
      acc[item.group].push(item);
      return acc;
    },
    {} as Record<string, typeof MOCK_HISTORY>,
  );

  return (
    <aside className="hidden lg:flex flex-col h-full w-72 bg-surface-container-lowest border-r border-outline-variant/20 py-4 shrink-0">
      {/* Các nút tạo mới */}
      <div className="px-4 mb-4">
        <button className="w-full flex items-center justify-center gap-2 bg-tertiary text-on-tertiary px-4 py-2.5 rounded-lg font-medium transition-transform active:scale-95 shadow-sm">
          <span className="material-symbols-outlined text-[20px]">add</span>
          <span>Cuộc hội thoại mới</span>
        </button>
        <button className="w-full mt-2 flex items-center justify-center gap-2 bg-white border border-tertiary/20 text-tertiary px-4 py-2.5 rounded-lg font-medium transition-transform active:scale-95 hover:bg-surface-container-low">
          <span className="material-symbols-outlined text-[20px]">
            note_add
          </span>
          <span>Tạo tài liệu mới</span>
        </button>
      </div>

      {/* Thanh tìm kiếm (Real-time) */}
      <div className="px-4 mb-4">
        <div className="flex items-center gap-1 bg-surface-container-low px-3 py-2 rounded-lg w-full focus-within:ring-2 focus-within:ring-tertiary/20 transition-all">
          <span className="material-symbols-outlined text-on-surface-variant text-[18px]">
            search
          </span>
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-transparent border-none focus:ring-0 text-sm w-full placeholder:text-on-surface-variant/60"
            placeholder="Search chats..."
            type="text"
          />
        </div>
      </div>

      {/* Danh sách lịch sử phân nhóm */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-2 space-y-6 pb-4">
        {Object.keys(groupedHistory).length === 0 ? (
          <p className="text-center text-xs text-on-surface-variant mt-10">
            Không tìm thấy kết quả
          </p>
        ) : (
          Object.entries(groupedHistory).map(([groupName, items]) => (
            <div key={groupName}>
              <h3 className="text-xs font-bold text-on-surface-variant uppercase tracking-wider px-2 mb-2">
                {groupName}
              </h3>
              <nav className="space-y-0.5">
                {items.map((item) => (
                  <a
                    key={item.id}
                    className={`block px-3 py-2 rounded-lg transition-colors ${item.active && !searchQuery ? "bg-surface-container" : "hover:bg-surface-container-low"}`}
                    href="#"
                  >
                    <p className="text-sm font-medium text-on-surface truncate">
                      {item.title}
                    </p>
                    <p className="text-[11px] text-on-surface-variant mt-0.5 truncate">
                      {item.preview}
                    </p>
                  </a>
                ))}
              </nav>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
