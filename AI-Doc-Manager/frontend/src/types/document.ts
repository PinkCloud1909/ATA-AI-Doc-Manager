// types/document.ts

export enum DocumentStatus {
  DRAFT          = "draft",
  PENDING_REVIEW = "pending_review",
  APPROVED       = "approved",
  REJECTED       = "rejected",
  EXPIRED        = "expired",
  ARCHIVED       = "archived",
}

export enum DocumentType {
  POLICY = "policy",
  MANUAL = "manual",
  REPORT = "report",
  OTHER  = "other",
}

export interface DocumentReview {
  id:            string
  document_id:   string
  grade:         number        // 1–10
  comment:       string
  user_id:       string
  reviewer_name?: string
  created_date:  string
}

export interface Document {
  id:                 string
  document_group_id:  string
  version:            number
  document_type:      DocumentType
  status:             DocumentStatus
  title:              string
  description?:       string | null

  // GCS: file_link là gs://bucket/path hoặc https://storage.googleapis.com/...
  file_link:          string
  original_filename:  string        // tên file gốc khi upload
  content_type:       string        // MIME type
  size_bytes?:        number

  is_vectorized:      boolean       // đã index vào Vertex AI Vector Search chưa
  vertex_index_id?:   string        // Vertex AI Matching Engine index ID

  created_by?:        string | null
  created_by_name?:   string
  created_at:         string
  modified_by?:       string
  modified_date?:     string

  reviews?:           DocumentReview[]
  avg_grade?:         number
}

export interface DocumentListItem {
  id:                string
  document_id?:      string
  document_group_id: string
  version:           number
  document_type:     DocumentType
  status:            DocumentStatus
  title:             string
  description?:      string | null
  file_link:         string
  original_filename: string
  size_bytes?:       number
  created_by_name:   string
  created_at:        string
  avg_grade?:        number
}

export interface DocumentListParams {
  status?:        DocumentStatus
  document_type?: DocumentType
  page?:          number
  page_size?:     number
  search?:        string
}

<<<<<<< Updated upstream
export interface PaginatedDocuments {
  items:     DocumentListItem[]
  total:     number
  page:      number
  page_size: number
=======
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
  created_by_name?: string | null;
  created_at?: string | null;
  average_review_grade?: number | null;
  review_count: number;
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
  preview_url: string;
  rag_ingestion_status: "not_ingested" | "pending" | "ingesting" | "completed" | "failed";
  rag_ingestion_error?: string | null;
  rag_ingested_at?: string | null;
  created_by?: string | null;
  created_by_name?: string | null;
  created_at?: string | null;
  modified_by?: string | null;
  modified_by_name?: string | null;
  modified_date?: string | null;
  submitted_by?: string | null;
  submitted_by_name?: string | null;
  submitted_at?: string | null;
  approved_by?: string | null;
  approved_by_name?: string | null;
  approved_at?: string | null;
  rejected_by?: string | null;
  rejected_by_name?: string | null;
  rejected_reason?: string | null;
  rejected_at?: string | null;
  average_review_grade?: number | null;
  review_count: number;
}

// ── Approvals ─────────────────────────────────────────────────────────────────

/** Item in the pending-approval queue (GET /api/v1/approvals/pending) */
export interface ApprovalQueueItem {
  document_id: string;
  document_group_id: string;
  version: number;
  title: string;
  document_type: DocumentType;
  status: Status;
  created_by?: string | null;
  created_by_name?: string | null;
  created_at?: string | null;
  submitted_by?: string | null;
  submitted_by_name?: string | null;
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
  user_name?: string | null;
  grade: number;
  comment: string;
  created_date?: string | null;
}

export interface ReviewListResponse {
  items: ReviewResponse[];
  total: number;
  page: number;
  page_size: number;
>>>>>>> Stashed changes
}
