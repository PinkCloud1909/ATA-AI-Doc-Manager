// types/vectorization.ts
// Aligned with OpenAPI schemas

/** POST /api/v1/vectorization/bulk request body */
export interface BulkVectorizationRequest {
  document_ids: string[];
}

/** Single-document vectorization result (sync mode) */
export interface VectorizationResponse {
  document_id: string;
  is_vectorized: boolean;
  chunk_count: number;
  processing_time_ms: number;
  message: string;
}

/** Aggregated bulk results (sync mode) */
export interface BulkVectorizationResponse {
  results: VectorizationResponse[];
  total_processed: number;
  total_failed: number;
}

/** Single-document task accepted (Cloud Tasks async mode) */
export interface TaskAcceptedResponse {
  document_id: string;
  message: string;
  task_name: string;
}

/** Bulk task accepted (Cloud Tasks async mode) */
export interface BulkTaskAcceptedResponse {
  accepted: string[];
  failed: string[];
  message: string;
}

/** GET /api/v1/vectorization/{id}/status response */
export interface VectorizationStatusResponse {
  document_id: string;
  is_vectorized: boolean;
  title: string;
  content_type?: string | null;
}
