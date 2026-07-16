// types/chat.ts
// Aligned with OpenAPI schemas: ChatRequest, ChatResponse

export type MessageRole = "user" | "assistant";

/** POST /api/v1/qa/chat request body */
export interface ChatRequest {
  message: string;
  session_id?: string | null;
}

/** POST /api/v1/qa/chat response */
export interface ChatResponse {
  session_id: string;
  response: string;
}

// ── Client-side display types ────────────────────────────────────────────────

/** Reference to a source document returned by the RAG search tool */
export interface SourceReference {
  document_id?: string;
  original_filename?: string;
  score?: number;
  title?: string;
  chunk_index?: number;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  is_streaming?: boolean;
  sources?: SourceReference[];
}
