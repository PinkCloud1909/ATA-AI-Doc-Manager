"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { runbooksApi } from "@/lib/api/runbooks";
import type { RunbookGenerateRequest } from "@/types/runbook";

// ── Query key factory ───────────────────────────────────────────────────────

export const runbookKeys = {
  all: ["runbooks"] as const,
  lists: () => [...runbookKeys.all, "list"] as const,
  list: (params?: { page?: number; page_size?: number }) =>
    [...runbookKeys.lists(), params] as const,
  details: () => [...runbookKeys.all, "detail"] as const,
  detail: (id: string) => [...runbookKeys.details(), id] as const,
};

// ── Queries ─────────────────────────────────────────────────────────────────

export function useRunbookList(params?: {
  page?: number;
  page_size?: number;
}) {
  return useQuery({
    queryKey: runbookKeys.list(params),
    queryFn: () => runbooksApi.list(params),
  });
}

export function useRunbook(id: string) {
  return useQuery({
    queryKey: runbookKeys.detail(id),
    queryFn: () => runbooksApi.getById(id),
    enabled: Boolean(id),
  });
}

// ── Mutations ───────────────────────────────────────────────────────────────

export function useGenerateRunbook() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: RunbookGenerateRequest) =>
      runbooksApi.generate(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: runbookKeys.lists() });
    },
  });
}

export function useDeleteRunbook() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => runbooksApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: runbookKeys.lists() });
    },
  });
}
