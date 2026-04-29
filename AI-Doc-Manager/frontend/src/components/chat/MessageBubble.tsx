import { ChatMessage } from "@/types/chat";
import { SourceCitation } from "./SourceCitation";
/*
export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user"

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[80%] space-y-2 ${isUser ? "items-end" : "items-start"} flex flex-col`}>
        {/* Bubble */ /*}
        <div
          className={`px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap
            ${isUser
              ? "bg-blue-600 text-white rounded-br-sm"
              : "bg-slate-100 text-slate-800 rounded-bl-sm"
            }`}
        >
          {message.content}
          {message.is_streaming && (
            <span className="inline-block w-1.5 h-4 bg-current ml-1 animate-pulse rounded-sm" />
          )}
        </div>

        {/* Sources */ /*}
        {message.sources && message.sources.length > 0 && (
          <SourceCitation sources={message.sources} isFromKb={message.is_from_kb ?? false} />
        )}

        {/* Timestamp */ /*}
        <span className="text-xs text-slate-400 px-1">
          {new Date(message.timestamp).toLocaleTimeString("vi-VN", {
            hour:   "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
    </div>
  )
}
*/
import React from "react";

interface MessageBubbleProps {
  role: "user" | "ai";
  timestamp: string;
  badgeType?: "generated" | "trusted"; // Phân biệt loại phản hồi của AI
  children: React.ReactNode;
}

export default function MessageBubble({
  role,
  timestamp,
  badgeType,
  children,
}: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div
      className={`max-w-3xl mx-auto flex flex-col ${isUser ? "items-end animate-in fade-in slide-in-from-bottom-2 duration-500" : "items-start"}`}
    >
      {/* Header cho tin nhắn AI (Icon & Badge) */}
      {!isUser && badgeType === "generated" && (
        <div className="flex items-center gap-2 mb-2">
          <div className="w-6 h-6 rounded-md bg-tertiary-container flex items-center justify-center">
            <span
              className="material-symbols-outlined text-white text-[14px]"
              style={{ fontVariationSettings: '"FILL" 1' }}
            >
              auto_awesome
            </span>
          </div>
          <span className="text-[11px] font-bold tracking-widest uppercase text-tertiary-fixed">
            AI GENERATED
          </span>
        </div>
      )}
      {!isUser && badgeType === "trusted" && (
        <div className="flex items-center gap-2 mb-2">
          <div className="w-6 h-6 rounded-md bg-green-100 flex items-center justify-center">
            <span
              className="material-symbols-outlined text-green-700 text-[14px]"
              style={{ fontVariationSettings: '"FILL" 1' }}
            >
              verified
            </span>
          </div>
          <span className="text-[11px] font-bold tracking-widest uppercase text-green-700">
            TỪ TÀI LIỆU ĐÃ DUYỆT
          </span>
        </div>
      )}

      {/* Nội dung tin nhắn */}
      <div
        className={
          isUser
            ? "bg-surface-container-low text-on-surface px-5 py-3 rounded-2xl rounded-tr-none shadow-sm max-w-[85%]"
            : "bg-surface-container-lowest border border-surface-container-high/30 p-5 rounded-2xl rounded-tl-none shadow-sm space-y-4 w-full"
        }
      >
        {children}
      </div>

      {/* Thời gian */}
      <span className="text-[10px] text-on-surface-variant mt-2 font-medium">
        {timestamp}
      </span>
    </div>
  );
}
