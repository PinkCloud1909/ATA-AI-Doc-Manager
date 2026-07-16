/**
 * lib/api/chat.ts
 *
 * Backend API:
 *  - POST /api/v1/qa/chat          — RAG-powered Q&A (non-streaming)
 */

import apiClient from "./client"
import { ChatRequest, ChatResponse } from "@/types/chat"

export const chatApi = {

  // ── Q&A Chat (RAG-powered via ADK agent + Google Cloud RAG Engine) ─────────
  sendMessage: async (payload: ChatRequest): Promise<ChatResponse> => {
    const { data } = await apiClient.post<ChatResponse>("/qa/chat", payload)
    return data
  },
}

// Re-export for backward compatibility
export const qaApi = chatApi
