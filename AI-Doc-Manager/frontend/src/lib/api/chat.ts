/**
 * lib/api/chat.ts
 *
 * Chat endpoint vẫn là FastAPI, nhưng backend giờ dùng:
 *  - Vertex AI Vector Search thay vì ChromaDB
 *  - Google ADK + Gemini thay vì gọi Gemini trực tiếp
 *
 * Frontend không thay đổi nhiều — chỉ cần lưu ý:
 *  - WebSocket trên Cloud Run cần sticky session (Cloud Run hỗ trợ via header)
 *  - Token Firebase được gửi qua query param vì WS không hỗ trợ custom header
 */

import apiClient from "./client"
import { getCurrentIdToken } from "@/lib/auth/firebase"
import { ChatRequest, ChatResponse } from "@/types/chat"

const WS_BASE =
  process.env.NEXT_PUBLIC_WS_URL ??
  (typeof window !== "undefined"
    ? `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/api/v1`
    : "ws://localhost:8000/api/v1")

export const chatApi = {

  // ── REST (non-streaming, dùng cho mobile hoặc fallback) ───────────────────
  sendMessage: async (payload: ChatRequest): Promise<ChatResponse> => {
    const { data } = await apiClient.post<ChatResponse>("/chat", payload)
    return data
  },

  // ── WebSocket Streaming ───────────────────────────────────────────────────
  /**
   * Tạo WebSocket connection với Firebase ID Token.
   * Cloud Run: cần đảm bảo backend service allow WebSocket
   * và set --concurrency đủ cao (hoặc dùng Session Affinity).
   */
  createStreamingConnection: async (
    sessionId: string,
    handlers: {
      onToken:   (token: string) => void
      onSources: (sources: ChatResponse["sources"], isFromKb: boolean) => void
      onDone:    () => void
      onError:   (err: Event) => void
    },
  ): Promise<WebSocket> => {
    // Firebase ID Token trong query param (WS không có Authorization header)
    const idToken = await getCurrentIdToken()
    const ws = new WebSocket(
      `${WS_BASE}/chat/ws/${sessionId}?token=${idToken ?? ""}`,
    )

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data as string)
        switch (msg.type) {
          case "token":   handlers.onToken(msg.content);                          break
          case "sources": handlers.onSources(msg.sources, msg.is_from_kb);       break
          case "done":    handlers.onDone();                                       break
          case "error":   handlers.onError(new Event(msg.message));              break
        }
      } catch {
        handlers.onToken(event.data as string)
      }
    }

    ws.onerror  = handlers.onError
    ws.onclose  = (e) => { if (!e.wasClean) handlers.onError(new Event("ws_closed")) }

    return ws
  },

  // ── Generate Runbook ──────────────────────────────────────────────────────
  generateRunbook: async (prompt: string, documentType: string) => {
    const { data } = await apiClient.post("/generate/runbook", {
      prompt,
      document_type: documentType,
    })
    return data
  },
}
