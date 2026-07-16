"use client";

import { create } from "zustand";
import type { ChatMessage } from "@/types/chat";
import { v4 as uuid } from "uuid";

interface ChatState {
  sessionId: string;
  messages: ChatMessage[];
  isStreaming: boolean;

  addMessage: (msg: ChatMessage) => void;
  updateMessage: (
    id: string,
    patch: Partial<Pick<ChatMessage, "content" | "is_streaming">>,
  ) => void;
  setStreaming: (v: boolean) => void;
  setSessionId: (id: string) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>()((set) => ({
  sessionId: uuid(),
  messages: [],
  isStreaming: false,

  addMessage: (msg) =>
    set((s) => ({ messages: [...s.messages, msg] })),

  updateMessage: (id, patch) =>
    set((s) => ({
      messages: s.messages.map((m) =>
        m.id === id ? { ...m, ...patch } : m,
      ),
    })),

  setStreaming: (v) => set({ isStreaming: v }),

  setSessionId: (id) => set({ sessionId: id }),

  clearMessages: () => set({ messages: [], sessionId: uuid() }),
}));
