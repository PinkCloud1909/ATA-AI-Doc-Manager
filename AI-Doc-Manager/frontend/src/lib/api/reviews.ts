/**
 * lib/api/reviews.ts
 *
 * Backend endpoints:
 *  POST /api/v1/documents/{id}/reviews  → ReviewResponse
 *  GET  /api/v1/documents/{id}/reviews  → ReviewListResponse
 */

import apiClient from "./client";
import type {
  ReviewCreateRequest,
  ReviewResponse,
  ReviewListResponse,
} from "@/types/document";

export const reviewsApi = {
  create: async (
    documentId: string,
    grade: number,
    comment: string,
  ): Promise<ReviewResponse> => {
    const payload: ReviewCreateRequest = { grade, comment };
    const { data } = await apiClient.post<ReviewResponse>(
      `/documents/${documentId}/reviews`,
      payload,
    );
    return data;
  },

  list: async (
    documentId: string,
    params?: { page?: number; page_size?: number },
  ): Promise<ReviewListResponse> => {
    const { data } = await apiClient.get<ReviewListResponse>(
      `/documents/${documentId}/reviews`,
      { params },
    );
    return data;
  },
};
