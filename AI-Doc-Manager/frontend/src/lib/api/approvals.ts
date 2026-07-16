/**
 * lib/api/approvals.ts
 *
 * Backend endpoints:
 *  GET /api/v1/approvals/pending → ApprovalQueueItem[]
 */

import apiClient from "./client";
import type { ApprovalQueueItem } from "@/types/document";

export const approvalsApi = {
  pending: async (): Promise<ApprovalQueueItem[]> => {
    const { data } = await apiClient.get<ApprovalQueueItem[]>("/approvals/pending");
    return data;
  },
};
