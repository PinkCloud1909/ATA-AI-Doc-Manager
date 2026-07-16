/**
 * lib/api/vectorization.ts
 *
 * Backend endpoints:
 *  POST   /api/v1/vectorization/bulk?force=         → BulkVectorizationResponse | BulkTaskAcceptedResponse
 *  POST   /api/v1/vectorization/{id}?force=          → VectorizationResponse | TaskAcceptedResponse
 *  DELETE /api/v1/vectorization/{id}                 → VectorizationResponse
 *  GET    /api/v1/vectorization/{id}/status           → VectorizationStatusResponse
 */

import apiClient from "./client";
import type {
  BulkVectorizationRequest,
  BulkVectorizationResponse,
  BulkTaskAcceptedResponse,
  VectorizationResponse,
  TaskAcceptedResponse,
  VectorizationStatusResponse,
} from "@/types/vectorization";

export const vectorizationApi = {
  vectorize: async (
    documentId: string,
    force = false,
  ): Promise<VectorizationResponse | TaskAcceptedResponse> => {
    const { data } = await apiClient.post<
      VectorizationResponse | TaskAcceptedResponse
    >(`/vectorization/${documentId}`, null, { params: { force } });
    return data;
  },

  bulkVectorize: async (
    documentIds: string[],
    force = false,
  ): Promise<BulkVectorizationResponse | BulkTaskAcceptedResponse> => {
    const payload: BulkVectorizationRequest = { document_ids: documentIds };
    const { data } = await apiClient.post<
      BulkVectorizationResponse | BulkTaskAcceptedResponse
    >("/vectorization/bulk", payload, { params: { force } });
    return data;
  },

  deleteVectors: async (documentId: string): Promise<VectorizationResponse> => {
    const { data } = await apiClient.delete<VectorizationResponse>(
      `/vectorization/${documentId}`,
    );
    return data;
  },

  getStatus: async (
    documentId: string,
  ): Promise<VectorizationStatusResponse> => {
    const { data } = await apiClient.get<VectorizationStatusResponse>(
      `/vectorization/${documentId}/status`,
    );
    return data;
  },
};
