import apiClient from "./client"
import {
  Document,
  DocumentListItem,
  DocumentListParams,
  DocumentType,
  PaginatedDocuments,
} from "@/types/document"

export interface UploadDocumentPayload {
  file: File
  document_type: DocumentType
  title?: string
  description?: string
  document_group_id?: string
}

function toFormData(payload: UploadDocumentPayload): FormData {
  const form = new FormData()
  form.append("file", payload.file)
  form.append("document_type", payload.document_type)
  if (payload.title) form.append("title", payload.title)
  if (payload.description) form.append("description", payload.description)
  return form
}

export const documentsApi = {
  list: async (params?: DocumentListParams): Promise<PaginatedDocuments> => {
    const { data } = await apiClient.get<PaginatedDocuments>("/documents", {
      params,
    })
    return data
  },

  getById: async (id: string): Promise<Document> => {
    const { data } = await apiClient.get<Document>(`/documents/${id}`)
    return data
  },

  getVersionHistory: async (documentId: string): Promise<DocumentListItem[]> => {
    const { data } = await apiClient.get<DocumentListItem[]>(
      `/documents/${documentId}/versions`,
    )
    return data || []
  },

  getDownloadUrl: async (id: string): Promise<string> => {
    const { data } = await apiClient.get<{ download_url: string }>(
      `/documents/${id}/download-url`,
    )
    return data.download_url
  },

  create: async (
    file_link: string,
    document_type: DocumentType,
  ): Promise<Document> => {
    const { data } = await apiClient.post<Document>("/documents", {
      document_type,
      file_link,
    })
    return data
  },

  createVersion: async (
    documentId: string,
    file: File,
    title?: string,
    description?: string,
  ): Promise<Document> => {
    const form = new FormData()
    form.append("file", file)
    if (title) form.append("title", title)
    if (description) form.append("description", description)
    const { data } = await apiClient.post<Document>(
      `/documents/${documentId}/new-version`,
      form,
      { headers: { "Content-Type": "multipart/form-data" } },
    )
    return data
  },

  upload: async (
    payload: UploadDocumentPayload,
    onProgress?: (pct: number) => void,
  ): Promise<Document> => {
    if (payload.document_group_id) {
      return documentsApi.createVersion(
        payload.document_group_id,
        payload.file,
        payload.title,
        payload.description,
      )
    }

    const { data } = await apiClient.post<Document>(
      "/documents/upload",
      toFormData(payload),
      {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (event) => {
          if (event.total && onProgress) {
            onProgress(Math.round((event.loaded / event.total) * 100))
          }
        },
      },
    )
    return data
  },

  update: async (
    id: string,
    payload: Partial<Pick<Document, "title" | "description" | "document_type">>,
  ): Promise<Document> => {
    const { data } = await apiClient.put<Document>(`/documents/${id}`, payload)
    return data
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/documents/${id}`)
  },

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

  getAllReviews: async () => {
    const { data } = await apiClient.get("/reviews")
    return data || []
  },

  getPendingApprovals: async () => {
    const { data } = await apiClient.get("/approvals/pending")
    return data || []
  },

  getApprovedDocuments: async () => {
    const { data } = await apiClient.get("/approvals/approved")
    return data || []
  },

  getRejectedDocuments: async () => {
    const { data } = await apiClient.get("/approvals/rejected")
    return data || []
  },

  submitForReview: async (id: string) => {
    const { data } = await apiClient.post(`/documents/${id}/submit`)
    return data
  },

  approve: async (id: string) => {
    const { data } = await apiClient.post(`/documents/${id}/approve`)
    return data
  },

  reject: async (id: string, reason: string) => {
    const { data } = await apiClient.post(`/documents/${id}/reject`, { reason })
    return data
  },
}
