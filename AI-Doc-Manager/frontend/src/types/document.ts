// types/document.ts
// Aligned with OpenAPI schemas — single source of truth

// ── Enums ─────────────────────────────────────────────────────────────────────

export type DocumentType = "policy" | "manual" | "report" | "other";
export type Status =
  | "draft"
  | "pending_review"
  | "approved"
  | "rejected"
  | "expired"
  | "active"
  | "archived";

// ── Request types ──────────────────────────────────────────────────────────────

export interface DocumentUpdateRequest {
  title?: string | null;
  description?: string | null;
  document_type?: DocumentType | null;
}

export interface RejectRequest {
  reason: string;
}

export interface DocumentListParams {
  page?: number;
  page_size?: number;
  status_filter?: Status | null;
  /** @deprecated Use status_filter instead */
  status?: Status | null;
  document_type?: DocumentType | null;
  created_by?: string | null;
}

// ── Response types ─────────────────────────────────────────────────────────────

/** Returned by POST /api/v1/documents/upload and new-version */
export interface DocumentUploadResponse {
  document_id: string;
  document_group_id: string;
  version: number;
  title: string;
  original_filename: string;
  document_type: DocumentType;
  status: Status;
  file_size?: number | null;
  content_type?: string | null;
  created_by?: string | null;
  created_at?: string | null;
}

/** Returned by workflow actions: submit, approve, reject, expire */
export interface DocumentActionResponse {
  document_id: string;
  document_group_id: string;
  version: number;
  document_type: DocumentType;
  status: Status;
  submitted_by?: string | null;
  submitted_at?: string | null;
  approved_by?: string | null;
  approved_at?: string | null;
  rejected_by?: string | null;
  rejected_reason?: string | null;
  rejected_at?: string | null;
}

/** Returned by DELETE endpoints */
export interface DocumentDeleteResponse {
  detail: string;
  document_id: string;
}

/** Lightweight item in list views (GET /api/v1/documents) */
export interface DocumentListItem {
  document_id: string;
  document_group_id: string;
  version: number;
  title: string;
  original_filename: string;
  document_type: DocumentType;
  status: Status;
  file_size?: number | null;
  content_type?: string | null;
  created_by?: string | null;
  created_at?: string | null;
}

/** Paginated document list */
export interface DocumentListResponse {
  items: DocumentListItem[];
  total: number;
  page: number;
  page_size: number;
}

/** Full document detail (GET /api/v1/documents/{id}) */
export interface DocumentDetailResponse {
  document_id: string;
  document_group_id: string;
  version: number;
  title: string;
  description?: string | null;
  original_filename: string;
  document_type: DocumentType;
  status: Status;
  file_size?: number | null;
  content_type?: string | null;
  download_url: string;
  is_vectorized?: boolean | null;
  created_by?: string | null;
  created_at?: string | null;
  modified_by?: string | null;
  modified_date?: string | null;
  submitted_by?: string | null;
  submitted_at?: string | null;
  approved_by?: string | null;
  approved_at?: string | null;
  rejected_by?: string | null;
  rejected_reason?: string | null;
  rejected_at?: string | null;
}

// ── Approvals ─────────────────────────────────────────────────────────────────

/** Item in the pending-approval queue (GET /api/v1/approvals/pending) */
export interface ApprovalQueueItem {
  document_id: string;
  document_group_id: string;
  version: number;
  document_type: DocumentType;
  status: Status;
  created_by?: string | null;
  created_at?: string | null;
  submitted_by?: string | null;
  submitted_at?: string | null;
}

// ── Reviews ───────────────────────────────────────────────────────────────────

export interface ReviewCreateRequest {
  grade: number; // 1–10
  comment: string; // 1–2000 chars
}

export interface ReviewResponse {
  id: string;
  document_id: string;
  user_id: string;
  grade: number;
  comment: string;
  created_date?: string | null;
}

export interface ReviewListResponse {
  items: ReviewResponse[];
  total: number;
  page: number;
  page_size: number;
}
