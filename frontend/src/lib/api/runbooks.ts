/**
 * lib/api/runbooks.ts
 *
 * Backend endpoints:
 *  POST   /api/v1/runbooks/generate  → RunbookResponse
 *  GET    /api/v1/runbooks           → RunbookListResponse
 *  GET    /api/v1/runbooks/{id}      → RunbookResponse
 *  DELETE /api/v1/runbooks/{id}      → RunbookDeleteResponse
 */

import apiClient from "./client";
import type {
  RunbookGenerateRequest,
  RunbookResponse,
  RunbookListResponse,
  RunbookDeleteResponse,
} from "@/types/runbook";

export const runbooksApi = {
  generate: async (payload: RunbookGenerateRequest): Promise<RunbookResponse> => {
    const { data } = await apiClient.post<RunbookResponse>(
      "/runbooks/generate",
      payload,
    );
    return data;
  },

  list: async (params?: {
    page?: number;
    page_size?: number;
  }): Promise<RunbookListResponse> => {
    const { data } = await apiClient.get<RunbookListResponse>("/runbooks", {
      params,
    });
    return data;
  },

  getById: async (id: string): Promise<RunbookResponse> => {
    const { data } = await apiClient.get<RunbookResponse>(`/runbooks/${id}`);
    return data;
  },

  delete: async (id: string): Promise<RunbookDeleteResponse> => {
    const { data } = await apiClient.delete<RunbookDeleteResponse>(
      `/runbooks/${id}`,
    );
    return data;
  },
};
