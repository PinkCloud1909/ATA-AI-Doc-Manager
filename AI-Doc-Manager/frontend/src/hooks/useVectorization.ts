"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { vectorizationApi } from "@/lib/api/vectorization";
import { documentKeys } from "./useDocuments";

// ── Query key factory ───────────────────────────────────────────────────────

export const vectorizationKeys = {
  all: ["vectorization"] as const,
  status: (documentId: string) =>
    [...vectorizationKeys.all, "status", documentId] as const,
};

// ── Queries ─────────────────────────────────────────────────────────────────

export function useVectorizationStatus(documentId: string) {
  return useQuery({
    queryKey: vectorizationKeys.status(documentId),
    queryFn: () => vectorizationApi.getStatus(documentId),
    enabled: Boolean(documentId),
  });
}

// ── Mutations ───────────────────────────────────────────────────────────────

export function useVectorizeDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      documentId,
      force,
    }: {
      documentId: string;
      force?: boolean;
    }) => vectorizationApi.vectorize(documentId, force),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({
        queryKey: vectorizationKeys.status(vars.documentId),
      });
      qc.invalidateQueries({ queryKey: documentKeys.detail(vars.documentId) });
      qc.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}

export function useBulkVectorize() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      documentIds,
      force,
    }: {
      documentIds: string[];
      force?: boolean;
    }) => vectorizationApi.bulkVectorize(documentIds, force),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: documentKeys.lists() });
      qc.invalidateQueries({ queryKey: vectorizationKeys.all });
    },
  });
}

export function useDeleteVectors() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (documentId: string) =>
      vectorizationApi.deleteVectors(documentId),
    onSuccess: (_, documentId) => {
      qc.invalidateQueries({
        queryKey: vectorizationKeys.status(documentId),
      });
      qc.invalidateQueries({ queryKey: documentKeys.detail(documentId) });
      qc.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}
