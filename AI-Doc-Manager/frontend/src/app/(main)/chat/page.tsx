"use client"

import { useEffect, useRef, useState } from "react"
import MessageBubble from "@/components/chat/MessageBubble"
import ChatInput from "@/components/chat/ChatInput"
import ChatSidebar from "@/components/chat/ChatSidebar"
import { SourceCitation } from "@/components/chat/SourceCitation"
import { chatApi } from "@/lib/api/chat"
import { SourceReference } from "@/types/chat"

interface UiMessage {
  id: string
  role: "user" | "ai"
  text: string
  timestamp: string
  badgeType?: "generated" | "trusted"
  sources?: SourceReference[]
  isFromKb?: boolean
}

function now() {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  })
}

export default function ChatPage() {
  const [messages, setMessages] = useState<UiMessage[]>([
    {
      id: "welcome",
      role: "ai",
      text: "Chào bạn. Hãy hỏi về tài liệu đã approved hoặc yêu cầu tạo runbook mới.",
      timestamp: now(),
      badgeType: "generated",
    },
  ])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isLoading])

  const handleSendMessage = async (
    text: string,
    mode: "text" | "voice" = "text",
  ) => {
    const sessionId = "default-session"
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", text, timestamp: now() },
    ])
    setIsLoading(true)

    try {
      const response = await chatApi.sendMessage({
        message: text,
        session_id: sessionId,
        mode,
      })
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "ai",
          text: response.answer ?? response.response,
          timestamp: now(),
          badgeType: response.is_from_kb ? "trusted" : "generated",
          sources: response.sources,
          isFromKb: response.is_from_kb,
        },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "ai",
          text: "Không gọi được backend chat. Kiểm tra FastAPI ở port 8000 rồi thử lại.",
          timestamp: now(),
          badgeType: "generated",
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-full w-full overflow-hidden bg-background">
      <ChatSidebar />
      <main className="relative flex h-full flex-1 flex-col overflow-hidden">
        <div className="custom-scrollbar flex-1 space-y-8 overflow-y-auto px-6 py-8">
          {messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              role={msg.role}
              timestamp={msg.timestamp}
              badgeType={msg.badgeType}
            >
              <p className="whitespace-pre-wrap text-[15px] leading-relaxed text-on-surface">
                {msg.text}
              </p>
              {msg.sources && (
                <SourceCitation
                  sources={msg.sources}
                  isFromKb={msg.isFromKb ?? false}
                />
              )}
            </MessageBubble>
          ))}
          {isLoading && (
            <MessageBubble role="ai" timestamp={now()} badgeType="generated">
              <p className="text-sm text-on-surface-variant">Đang xử lý...</p>
            </MessageBubble>
          )}
          <div ref={messagesEndRef} />
        </div>
        <ChatInput onSendMessage={handleSendMessage} />
      </main>
    </div>
  )
}
