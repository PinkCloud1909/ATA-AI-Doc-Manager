"use client"

import { useRef, useCallback } from "react"
import { useChatStore } from "@/stores/chatStore"
import { chatApi } from "@/lib/api/chat"

export function useChat() {
  const store    = useChatStore()
  const wsRef    = useRef<WebSocket | null>(null)
  const msgIdRef = useRef<string | null>(null)

  const sendMessage = useCallback(
    async (content: string) => {
      if (store.isStreaming) return

      store.addUserMessage(content)
      const assistantId = store.startAssistantMessage()
      msgIdRef.current  = assistantId

      wsRef.current?.close()

      // createStreamingConnection là async vì cần await Firebase token
      const ws = await chatApi.createStreamingConnection(store.sessionId, {
        onToken: (token) => {
          if (msgIdRef.current) store.appendToken(msgIdRef.current, token)
        },
        onSources: (sources, isFromKb) => {
          if (msgIdRef.current)
            store.finalizeMessage(msgIdRef.current, sources, isFromKb)
        },
        onDone: () => {
          store.setStreaming(false)
          wsRef.current?.close()
        },
        onError: () => store.setStreaming(false),
      })

      wsRef.current = ws
      ws.onopen = () => {
        ws.send(JSON.stringify({ message: content, session_id: store.sessionId }))
      }
    },
    [store],
  )

  const stopStreaming = useCallback(() => {
    wsRef.current?.close()
    store.setStreaming(false)
  }, [store])

  return {
    messages:    store.messages,
    isStreaming: store.isStreaming,
    sessionId:   store.sessionId,
    sendMessage,
    stopStreaming,
    clearConversation: store.clearConversation,
    newSession:        store.newSession,
  }
}
