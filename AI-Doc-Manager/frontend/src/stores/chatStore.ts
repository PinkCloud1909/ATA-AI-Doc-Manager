"use client"

import { create } from "zustand"
import { ChatMessage, SourceReference } from "@/types/chat"
import { v4 as uuid } from "uuid"

interface ChatState {
  sessionId:   string
  messages:    ChatMessage[]
  isStreaming: boolean

  addUserMessage:    (content: string) => void
  startAssistantMessage: () => string
  appendToken:       (id: string, token: string) => void
  finalizeMessage:   (id: string, sources: SourceReference[], isFromKb: boolean) => void
  setStreaming:      (v: boolean) => void
  clearConversation: () => void
  newSession:        () => void
}

export const useChatStore = create<ChatState>((set) => ({
  sessionId:   uuid(),
  messages:    [],
  isStreaming: false,

  addUserMessage: (content) =>
    set((s) => ({
      messages: [...s.messages, { id: uuid(), role: "user", content, timestamp: new Date().toISOString() }],
    })),

  startAssistantMessage: () => {
    const id = uuid()
    set((s) => ({
      messages: [...s.messages, { id, role: "assistant", content: "", timestamp: new Date().toISOString(), is_streaming: true }],
      isStreaming: true,
    }))
    return id
  },

  appendToken: (id, token) =>
    set((s) => ({
      messages: s.messages.map((m) => m.id === id ? { ...m, content: m.content + token } : m),
    })),

  finalizeMessage: (id, sources, isFromKb) =>
    set((s) => ({
      messages: s.messages.map((m) =>
        m.id === id ? { ...m, sources, is_from_kb: isFromKb, is_streaming: false } : m,
      ),
      isStreaming: false,
    })),

  setStreaming:      (v) => set({ isStreaming: v }),
  clearConversation: ()  => set({ messages: [] }),
  newSession:        ()  => set({ sessionId: uuid(), messages: [], isStreaming: false }),
}))
