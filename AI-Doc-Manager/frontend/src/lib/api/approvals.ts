import apiClient from "./client"
import { DocumentListItem } from "@/types/document"

export const approvalsApi = {
  getPendingQueue: async (): Promise<DocumentListItem[]> => {
    const { data } = await apiClient.get<{ items: DocumentListItem[] }>("/documents", {
      params: { status: "PENDING_REVIEW", page_size: 100 },
    })
    return data.items ?? data
  },

  submit:  async (id: string)              => apiClient.post(`/documents/${id}/submit`),
  approve: async (id: string)              => apiClient.post(`/documents/${id}/approve`),
  reject:  async (id: string, reason: string) =>
    apiClient.post(`/documents/${id}/reject`, { reason }),
}
