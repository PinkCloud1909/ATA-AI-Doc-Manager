export type RagIngestionStatus =
  | "not_ingested"
  | "pending"
  | "ingesting"
  | "completed"
  | "failed";

export interface RagStatusResponse {
  document_id: string;
  status: RagIngestionStatus;
  error_message?: string | null;
  rag_ingested_at?: string | null;
  title?: string | null;
  content_type?: string | null;
}

export interface RagActionResponse {
  document_id: string;
  status?: RagIngestionStatus;
  message: string;
  task_name?: string | null;
}
