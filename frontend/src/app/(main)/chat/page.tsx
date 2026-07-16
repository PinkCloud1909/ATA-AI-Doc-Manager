"use client";

import { useRef, useEffect } from "react";
import { useTranslation } from "@/i18n/LanguageContext";
import MessageBubble from "@/components/chat/MessageBubble";
import ChatInput from "@/components/chat/ChatInput";
import ChatSidebar from "@/components/chat/ChatSidebar";
import { useChatStore } from "@/stores/chatStore";
import { useChat } from "@/hooks/useChat";

export default function ChatPage() {
  const { t } = useTranslation();
  const messages = useChatStore((s) => s.messages);
  const isStreaming = useChatStore((s) => s.isStreaming);
  const { sendMessage } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex h-full w-full overflow-hidden bg-background relative">
      <ChatSidebar />

      <main className="flex-1 flex flex-col h-full relative overflow-hidden">
        <div className="flex-1 overflow-y-auto px-6 py-8 space-y-10 custom-scrollbar">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center">
              <div className="flex flex-col items-center gap-3 text-center">
                <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-surface-container-low text-tertiary">
                  <span className="material-symbols-outlined text-[30px]">
                    auto_awesome
                  </span>
                </div>
                <h2 className="text-xl font-bold text-on-surface">
                  {t.chat.welcomeTitle}
                </h2>
                <p className="text-sm text-on-surface-variant max-w-md">
                  {t.chat.welcomeDescription}
                </p>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                role={msg.role === "user" ? "user" : "ai"}
                timestamp={new Date(msg.timestamp).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
                badgeType="generated"
              >
                <p className="text-[15px] leading-relaxed text-on-surface whitespace-pre-wrap">
                  {msg.is_streaming && !msg.content ? "..." : msg.content}
                </p>
              </MessageBubble>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
        <ChatInput onSendMessage={sendMessage} disabled={isStreaming} />
      </main>
    </div>
  );
}
