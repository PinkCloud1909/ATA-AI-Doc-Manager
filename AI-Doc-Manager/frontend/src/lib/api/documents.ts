/**
 * lib/api/documents.ts
 *
 * Thay đổi so với kiến trúc MinIO:
 *  - Upload dùng 2 bước: signed-upload-url → PUT GCS → confirm-upload
 *  - file_link trả về là GCS path (gs://bucket/path) hoặc public HTTPS URL
 *  - Download dùng signed URL (nếu bucket private) hoặc public URL (nếu public)
 */

import apiClient from "./client"
import { uploadToGcs, SignedUploadUrlResponse } from "@/lib/gcs"
import {
  Document,
  DocumentListItem,
  DocumentListParams,
  PaginatedDocuments,
  DocumentType,
} from "@/types/document"

// ── Types ────────────────────────────────────────────────────────────────────

export interface UploadDocumentPayload {
  file:               File
  document_type:      DocumentType
  document_group_id?: string     // omit = tài liệu mới; set = version mới
}

export interface ConfirmUploadPayload {
  gcs_path:           string
  original_filename:  string
  content_type:       string
  size_bytes:         number
  document_type:      DocumentType
  document_group_id?: string
}

// ── API ──────────────────────────────────────────────────────────────────────

export const documentsApi = {

  // ─── Listing & Detail ──────────────────────────────────────────────────────

  list: async (params?: DocumentListParams): Promise<PaginatedDocuments> => {
    const { data } = await apiClient.get<PaginatedDocuments>("/documents", { params })
    return data
  },

  getById: async (id: string): Promise<Document> => {
    const { data } = await apiClient.get<Document>(`/documents/${id}`)
    return data
  },

  getVersionHistory: async (groupId: string): Promise<DocumentListItem[]> => {
    const { data } = await apiClient.get<DocumentListItem[]>(
      `/documents/group/${groupId}`,
    )
    return data
  },

  // ─── GCS Upload (2-step) ───────────────────────────────────────────────────

  /**
   * Bước 1: Yêu cầu backend tạo Signed URL
   */
  getSignedUploadUrl: async (
    filename: string,
    contentType: string,
  ): Promise<SignedUploadUrlResponse> => {
    const { data } = await apiClient.post<SignedUploadUrlResponse>(
      "/documents/signed-upload-url",
      { filename, content_type: contentType },
    )
    return data
  },

  /**
   * Bước 2 + 3: Upload lên GCS rồi confirm với backend
   */
  upload: async (
    payload: UploadDocumentPayload,
    onProgress?: (pct: number) => void,
  ): Promise<Document> => {
    // 1. Lấy Signed URL từ backend
    const { signed_url, gcs_path } = await documentsApi.getSignedUploadUrl(
      payload.file.name,
      payload.file.type,
    )

    // 2. PUT file trực tiếp lên GCS (bypass backend → giảm tải, tăng tốc)
    await uploadToGcs(signed_url, payload.file, onProgress)

    // 3. Báo backend lưu record vào PostgreSQL
    const { data } = await apiClient.post<Document>("/documents/confirm-upload", {
      gcs_path,
      original_filename:  payload.file.name,
      content_type:       payload.file.type,
      size_bytes:         payload.file.size,
      document_type:      payload.document_type,
      document_group_id:  payload.document_group_id,
    } satisfies ConfirmUploadPayload)

    return data
  },

  // ─── Download (Signed URL cho private bucket) ─────────────────────────────

  /**
   * Lấy Signed URL để download (TTL 15 phút).
   * Dùng khi bucket không public.
   */
  getDownloadUrl: async (id: string): Promise<string> => {
    const { data } = await apiClient.get<{ download_url: string }>(
      `/documents/${id}/download-url`,
    )
    return data.download_url
  },

  // ─── Delete ───────────────────────────────────────────────────────────────

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/documents/${id}`)
    // Backend sẽ xóa cả file trên GCS
  },

  // ─── Reviews ─────────────────────────────────────────────────────────────

  createReview: async (id: string, grade: number, comment: string) => {
    const { data } = await apiClient.post(`/documents/${id}/reviews`, {
      grade,
      comment,
    })
    return data
  },

  getReviews: async (id: string) => {
    const { data } = await apiClient.get(`/documents/${id}/reviews`)
    return data
  },
}
