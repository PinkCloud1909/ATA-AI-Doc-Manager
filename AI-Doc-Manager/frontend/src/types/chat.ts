// types/chat.ts

export type ChatMode   = "text" | "voice"
export type MessageRole = "user" | "assistant"

export interface SourceReference {
  document_id:        string
  document_group_id:  string
  version:            number
  original_filename:  string
  gcs_path:           string         // gs://bucket/path
  download_url?:      string         // Signed URL (nếu có)

  // Vertex AI Vector Search metadata
  vertex_distance?:   number         // cosine distance (thấp = liên quan hơn)
  relevance_score?:   number         // 1 - distance (0–1, cao = liên quan hơn)
}

export interface ChatMessage {
  id:            string
  role:          MessageRole
  content:       string
  timestamp:     string
  sources?:      SourceReference[]
  is_from_kb?:   boolean             // true = từ Vertex AI search
  is_streaming?: boolean
}

export interface ChatRequest {
  message:    string
  session_id: string
  mode:       ChatMode
}

export interface ChatResponse {
  answer:      string
  sources:     SourceReference[]
  is_from_kb:  boolean
  session_id:  string
  model_used?: string                // e.g. "gemini-1.5-pro"
}
