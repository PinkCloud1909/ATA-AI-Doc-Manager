"use client";

import React, { useState } from "react";
import { useChatStore } from "@/stores/chatStore";
import { ChatSession } from "@/types/chat";

function startOfDay(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function getGroupLabel(updatedAt: string) {
  const date = new Date(updatedAt);
  if (Number.isNaN(date.getTime())) return "Cũ hơn";

  const today = startOfDay(new Date());
  const sessionDay = startOfDay(date);
  const diffDays = Math.round(
    (today.getTime() - sessionDay.getTime()) / 86_400_000,
  );

  if (diffDays === 0) return "Hôm nay";
  if (diffDays === 1) return "Hôm qua";
  if (diffDays < 7) return "7 ngày qua";

  return new Intl.DateTimeFormat("vi-VN", {
    month: "2-digit",
    year: "numeric",
  }).format(date);
}

function groupSessions(sessions: ChatSession[]) {
  return sessions.reduce(
    (acc, item) => {
      const group = getGroupLabel(item.updatedAt);
      if (!acc[group]) acc[group] = [];
      acc[group].push(item);
      return acc;
    },
    {} as Record<string, ChatSession[]>,
  );
}

export default function ChatSidebar() {
  const [searchQuery, setSearchQuery] = useState("");
  const history = useChatStore((s) => s.history);
  const sessionId = useChatStore((s) => s.sessionId);
  const isStreaming = useChatStore((s) => s.isStreaming);
  const newSession = useChatStore((s) => s.newSession);
  const loadSession = useChatStore((s) => s.loadSession);

  const filteredHistory = history.filter(
    (item) =>
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.preview.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const groupedHistory = groupSessions(filteredHistory);

  return (
    <aside className="flex flex-col h-full w-64 lg:w-72 border-r border-outline-variant/20 py-4 shrink-0 absolute lg:relative left-0 top-0 z-30 transition-all duration-300 bg-white/60 lg:bg-surface-container-lowest backdrop-blur-md lg:backdrop-blur-none hover:bg-surface-container-lowest focus-within:bg-surface-container-lowest shadow-[4px_0_24px_rgba(0,0,0,0.05)] lg:shadow-none">
      {/* Các nút tạo mới */}
      <div className="px-4 mb-4">
        <button
          type="button"
          onClick={newSession}
          disabled={isStreaming}
          className="w-full flex items-center justify-center gap-2 bg-tertiary text-on-tertiary px-4 py-2.5 rounded-lg font-medium transition-transform active:scale-95 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span className="material-symbols-outlined text-[20px]">add</span>
          <span>Cuộc hội thoại mới</span>
        </button>
      </div>

      {/* Thanh tìm kiếm (Real-time) */}
      <div className="px-4 mb-4">
        <div className="flex items-center gap-1 bg-surface-container-low px-3 py-2 rounded-lg w-full focus-within:ring-2 focus-within:ring-tertiary/20 transition-all shadow-inner">
          <span className="material-symbols-outlined text-on-surface-variant text-[18px]">
            search
          </span>
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-transparent border-none focus:ring-0 text-sm w-full placeholder:text-on-surface-variant/60"
            placeholder="Tìm kiếm hội thoại..."
            type="text"
          />
        </div>
      </div>

      {/* Danh sách lịch sử phân nhóm */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-2 space-y-6 pb-4">
        {Object.keys(groupedHistory).length === 0 ? (
          <p className="text-center text-xs text-on-surface-variant mt-10">
            {history.length === 0
              ? "Chưa có lịch sử trò chuyện"
              : "Không tìm thấy kết quả"}
          </p>
        ) : (
          Object.entries(groupedHistory).map(([groupName, items]) => (
            <div key={groupName}>
              <h3 className="text-xs font-bold text-on-surface-variant uppercase tracking-wider px-2 mb-2">
                {groupName}
              </h3>
              <nav className="space-y-0.5">
                {items.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    disabled={isStreaming}
                    onClick={() => loadSession(item.id)}
                    className={`block w-full text-left px-3 py-2 rounded-lg transition-colors disabled:cursor-not-allowed disabled:opacity-60 ${
                      item.id === sessionId
                        ? "bg-surface-container/80"
                        : "hover:bg-surface-container-low"
                    }`}
                  >
                    <p className="text-sm font-medium text-on-surface truncate">
                      {item.title}
                    </p>
                    <p className="text-[11px] text-on-surface-variant mt-0.5 truncate">
                      {item.preview}
                    </p>
                  </button>
                ))}
              </nav>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
