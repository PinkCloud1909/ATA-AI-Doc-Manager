"use client"

import { create } from "zustand"
import { persist } from "zustand/middleware"
import { ChatMessage, ChatSession, SourceReference } from "@/types/chat"
import { v4 as uuid } from "uuid"

const MAX_HISTORY_ITEMS = 50

function compactText(content: string) {
  return content.replace(/\s+/g, " ").trim()
}

function buildSession(id: string, messages: ChatMessage[]): ChatSession | null {
  if (messages.length === 0) return null

  const firstUserMessage = messages.find((message) => message.role === "user")
  const lastMessage = messages[messages.length - 1]
  const title = compactText(firstUserMessage?.content ?? "Cuộc hội thoại mới")
  const previewPrefix = lastMessage.role === "user" ? "You: " : "AI: "
  const preview = `${previewPrefix}${compactText(lastMessage.content)}`

  return {
    id,
    title: title.length > 64 ? `${title.slice(0, 61)}...` : title,
    preview: preview.length > 96 ? `${preview.slice(0, 93)}...` : preview,
    updatedAt: lastMessage.timestamp,
    messages,
  }
}

function upsertHistory(history: ChatSession[], session: ChatSession) {
  return [
    session,
    ...history.filter((item) => item.id !== session.id),
  ].slice(0, MAX_HISTORY_ITEMS)
}

interface ChatState {
  sessionId:   string
  messages:    ChatMessage[]
  history:     ChatSession[]
  isStreaming: boolean

  addUserMessage:    (content: string) => void
  startAssistantMessage: () => string
  appendToken:       (id: string, token: string) => void
  finalizeMessage:   (id: string, sources: SourceReference[], isFromKb: boolean) => void
  setStreaming:      (v: boolean) => void
  clearConversation: () => void
  saveCurrentSession: () => void
  loadSession:       (sessionId: string) => void
  newSession:        () => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      sessionId:   uuid(),
      messages:    [],
      history:     [],
      isStreaming: false,

      addUserMessage: (content) =>
        set((s) => ({
          messages: [
            ...s.messages,
            {
              id: uuid(),
              role: "user",
              content,
              timestamp: new Date().toISOString(),
            },
          ],
        })),

      startAssistantMessage: () => {
        const id = uuid()
        set((s) => ({
          messages: [
            ...s.messages,
            {
              id,
              role: "assistant",
              content: "",
              timestamp: new Date().toISOString(),
              is_streaming: true,
            },
          ],
          isStreaming: true,
        }))
        return id
      },

      appendToken: (id, token) =>
        set((s) => ({
          messages: s.messages.map((m) =>
            m.id === id ? { ...m, content: m.content + token } : m,
          ),
        })),

      finalizeMessage: (id, sources, isFromKb) =>
        set((s) => ({
          messages: s.messages.map((m) =>
            m.id === id
              ? { ...m, sources, is_from_kb: isFromKb, is_streaming: false }
              : m,
          ),
          isStreaming: false,
        })),

      setStreaming:      (v) => set({ isStreaming: v }),
      clearConversation: ()  => set({ messages: [] }),

      saveCurrentSession: () =>
        set((s) => {
          const session = buildSession(s.sessionId, s.messages)
          if (!session) return {}

          return { history: upsertHistory(s.history, session) }
        }),

      loadSession: (sessionId) =>
        set((s) => {
          if (sessionId === s.sessionId || s.isStreaming) return {}

          const targetSession = s.history.find((item) => item.id === sessionId)
          if (!targetSession) return {}

          const currentSession = buildSession(s.sessionId, s.messages)
          const history = currentSession
            ? upsertHistory(s.history, currentSession)
            : s.history

          return {
            sessionId: targetSession.id,
            messages: targetSession.messages,
            history,
            isStreaming: false,
          }
        }),

      newSession: () =>
        set((s) => {
          if (s.isStreaming) return {}

          const session = buildSession(s.sessionId, s.messages)
          return {
            sessionId: uuid(),
            messages: [],
            history: session ? upsertHistory(s.history, session) : s.history,
            isStreaming: false,
          }
        }),
    }),
    {
      name: "chat-history",
      partialize: (s) => ({
        sessionId: s.sessionId,
        messages: s.messages,
        history: s.history,
      }),
    },
  ),
)
