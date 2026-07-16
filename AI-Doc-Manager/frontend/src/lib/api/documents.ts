/**
 * lib/api/documents.ts
 *
 * Backend endpoints:
 *  POST   /api/v1/documents/upload              → DocumentUploadResponse
 *  GET    /api/v1/documents                     → DocumentListResponse
 *  GET    /api/v1/documents/{id}                → DocumentDetailResponse
 *  PUT    /api/v1/documents/{id}                → DocumentUploadResponse
 *  DELETE /api/v1/documents/{id}                → DocumentDeleteResponse (soft/archive)
 *  DELETE /api/v1/documents/{id}/permanent      → DocumentDeleteResponse
 *  POST   /api/v1/documents/{id}/new-version    → DocumentUploadResponse
 *  POST   /api/v1/documents/{id}/submit         → DocumentActionResponse
 *  POST   /api/v1/documents/{id}/approve        → DocumentActionResponse
 *  POST   /api/v1/documents/{id}/reject         → DocumentActionResponse
 *  POST   /api/v1/documents/{id}/expire         → DocumentActionResponse
 */

import apiClient from "./client";
import type {
  DocumentListParams,
  DocumentListResponse,
  DocumentDetailResponse,
  DocumentUploadResponse,
  DocumentActionResponse,
  DocumentDeleteResponse,
  DocumentUpdateRequest,
  RejectRequest,
  DocumentType,
} from "@/types/document";

export const documentsApi = {
  // ── Upload ────────────────────────────────────────────────────────────────

  upload: async (
    file: File,
    documentType: DocumentType = "other",
    title?: string,
    description?: string,
    onProgress?: (pct: number) => void,
  ): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("document_type", documentType);
    if (title) formData.append("title", title);
    if (description) formData.append("description", description);

    const { data } = await apiClient.post<DocumentUploadResponse>(
      "/documents/upload",
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (event) => {
          if (event.total && onProgress) {
            onProgress(Math.round((event.loaded * 100) / event.total));
          }
        },
      },
    );
    return data;
  },

  // ── List & Detail ─────────────────────────────────────────────────────────

  list: async (params?: DocumentListParams): Promise<DocumentListResponse> => {
    const { data } = await apiClient.get<DocumentListResponse>("/documents", {
      params,
    });
    return data;
  },

  getById: async (id: string): Promise<DocumentDetailResponse> => {
    const { data } = await apiClient.get<DocumentDetailResponse>(
      `/documents/${id}`,
    );
    return data;
  },

  // ── Update ────────────────────────────────────────────────────────────────

  update: async (
    id: string,
    payload: DocumentUpdateRequest,
  ): Promise<DocumentUploadResponse> => {
    const { data } = await apiClient.put<DocumentUploadResponse>(
      `/documents/${id}`,
      payload,
    );
    return data;
  },

  // ── New Version ───────────────────────────────────────────────────────────

  newVersion: async (
    documentId: string,
    file: File,
    title?: string,
    description?: string,
    onProgress?: (pct: number) => void,
  ): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    if (title) formData.append("title", title);
    if (description) formData.append("description", description);

    const { data } = await apiClient.post<DocumentUploadResponse>(
      `/documents/${documentId}/new-version`,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (event) => {
          if (event.total && onProgress) {
            onProgress(Math.round((event.loaded * 100) / event.total));
          }
        },
      },
    );
    return data;
  },

  // ── Workflow Actions ──────────────────────────────────────────────────────

  submitForReview: async (id: string): Promise<DocumentActionResponse> => {
    const { data } = await apiClient.post<DocumentActionResponse>(
      `/documents/${id}/submit`,
    );
    return data;
  },

  approve: async (id: string): Promise<DocumentActionResponse> => {
    const { data } = await apiClient.post<DocumentActionResponse>(
      `/documents/${id}/approve`,
    );
    return data;
  },

  reject: async (id: string, reason: string): Promise<DocumentActionResponse> => {
    const payload: RejectRequest = { reason };
    const { data } = await apiClient.post<DocumentActionResponse>(
      `/documents/${id}/reject`,
      payload,
    );
    return data;
  },

  expire: async (id: string): Promise<DocumentActionResponse> => {
    const { data } = await apiClient.post<DocumentActionResponse>(
      `/documents/${id}/expire`,
    );
    return data;
  },

  // ── Delete ────────────────────────────────────────────────────────────────

  /** Soft delete (archive) */
  archive: async (id: string): Promise<DocumentDeleteResponse> => {
    const { data } = await apiClient.delete<DocumentDeleteResponse>(
      `/documents/${id}`,
    );
    return data;
  },

  /** Hard delete (permanent — removes file + vectors) */
  hardDelete: async (id: string): Promise<DocumentDeleteResponse> => {
    const { data } = await apiClient.delete<DocumentDeleteResponse>(
      `/documents/${id}/permanent`,
    );
    return data;
  },
};
