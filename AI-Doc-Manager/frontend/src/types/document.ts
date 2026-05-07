// types/document.ts

export enum DocumentStatus {
  DRAFT          = "DRAFT",
  PENDING_REVIEW = "PENDING_REVIEW",
  APPROVED       = "APPROVED",
  REJECTED       = "REJECTED",
  EXPIRED        = "EXPIRED",
}

export enum DocumentType {
  TEMPLATE          = "TEMPLATE",
  CUSTOMER_SPECIFIC = "CUSTOMER_SPECIFIC",
  COMMON_GUIDE      = "COMMON_GUIDE",
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

  // GCS: file_link là gs://bucket/path hoặc https://storage.googleapis.com/...
  file_link:          string
  original_filename:  string        // tên file gốc khi upload
  content_type:       string        // MIME type
  size_bytes?:        number

  is_vectorized:      boolean       // đã index vào Vertex AI Vector Search chưa
  vertex_index_id?:   string        // Vertex AI Matching Engine index ID

  created_by:         string
  created_by_name?:   string
  created_at:         string
  modified_by?:       string
  modified_date?:     string

  reviews?:           DocumentReview[]
  avg_grade?:         number
}

export interface DocumentListItem {
  id:                string
  document_group_id: string
  version:           number
  document_type:     DocumentType
  status:            DocumentStatus
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

export interface PaginatedDocuments {
  items:     DocumentListItem[]
  total:     number
  page:      number
  page_size: number
}
