import apiClient from "./client";
import type { RagActionResponse, RagStatusResponse } from "@/types/rag";

export const ragApi = {
  status: async (documentId: string): Promise<RagStatusResponse> => {
    const { data } = await apiClient.get<RagStatusResponse>(`/rag/${documentId}/status`);
    return data;
  },

  ingest: async (documentId: string, force = false): Promise<RagActionResponse> => {
    const { data } = await apiClient.post<RagActionResponse>(
      `/rag/${documentId}`,
      undefined,
      { params: { force } },
    );
    return data;
  },

  remove: async (documentId: string): Promise<RagActionResponse> => {
    const { data } = await apiClient.delete<RagActionResponse>(`/rag/${documentId}`);
    return data;
  },
};
