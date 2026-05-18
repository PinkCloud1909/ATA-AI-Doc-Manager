"use client"

import { useCallback } from "react"
import axios from "axios"
import { useChatStore } from "@/stores/chatStore"
import { qaApi } from "@/lib/api/chat"

function getChatErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as { detail?: string } | undefined
    return data?.detail ?? error.message
  }

  return error instanceof Error ? error.message : "Không thể kết nối chatbot."
}

export function useChat() {
  const store = useChatStore()

  const sendMessage = useCallback(
    async (content: string) => {
      if (store.isStreaming) return

      store.addUserMessage(content)
      const assistantId = store.startAssistantMessage()

      try {
        store.setStreaming(true)
        const response = await qaApi.chat({
          message: content,
          session_id: store.sessionId,
        })

        // Set the full response at once since it's non-streaming
        store.appendToken(assistantId, response.response)
        store.finalizeMessage(assistantId, [], false) // No sources for now
        store.setStreaming(false)
      } catch (error) {
        console.error("Chat error:", error)
        store.appendToken(assistantId, getChatErrorMessage(error))
        store.finalizeMessage(assistantId, [], false)
        store.setStreaming(false)
      }
    },
    [store],
  )

  const stopStreaming = useCallback(() => {
    store.setStreaming(false)
  }, [store])

  return {
    messages:          store.messages,
    isStreaming:       store.isStreaming,
    sessionId:         store.sessionId,
    sendMessage,
    stopStreaming,
    clearConversation: store.clearConversation,
    newSession:        store.newSession,
  }
}
