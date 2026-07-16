"use client";

import { useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import { chatApi } from "@/lib/api/chat";
import { useChatStore } from "@/stores/chatStore";
import type { ChatRequest } from "@/types/chat";
import { v4 as uuid } from "uuid";
import axios from "axios";

function getChatErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as { detail?: string } | undefined;
    return data?.detail ?? error.message;
  }
  return error instanceof Error ? error.message : "Không thể kết nối chatbot.";
}

export function useChat() {
  const store = useChatStore();

  const chatMutation = useMutation({
    mutationFn: (payload: ChatRequest) => chatApi.sendMessage(payload),
  });

  const sendMessage = useCallback(
    async (content: string) => {
      if (store.isStreaming) return;

      // Add user message
      store.addMessage({
        id: uuid(),
        role: "user",
        content,
        timestamp: new Date().toISOString(),
      });

      // Start assistant placeholder
      const assistantId = uuid();
      store.addMessage({
        id: assistantId,
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
        is_streaming: true,
      });
      store.setStreaming(true);

      try {
        const result = await chatMutation.mutateAsync({
          message: content,
          session_id: store.sessionId,
        });

        // Update session ID if changed
        if (result.session_id && result.session_id !== store.sessionId) {
          store.setSessionId(result.session_id);
        }

        // Replace the streaming placeholder with the final content
        store.updateMessage(assistantId, {
          content: result.response,
          is_streaming: false,
        });
      } catch (error) {
        store.updateMessage(assistantId, {
          content: getChatErrorMessage(error),
          is_streaming: false,
        });
      } finally {
        store.setStreaming(false);
      }
    },
    [store, chatMutation],
  );

  return {
    messages: store.messages,
    isStreaming: store.isStreaming,
    sessionId: store.sessionId,
    sendMessage,
    clearConversation: store.clearMessages,
  };
}
