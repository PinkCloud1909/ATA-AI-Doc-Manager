"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { documentsApi } from "@/lib/api/documents";
import { approvalsApi } from "@/lib/api/approvals";
import { reviewsApi } from "@/lib/api/reviews";
import type {
  DocumentListParams,
  DocumentType,
  DocumentUpdateRequest,
} from "@/types/document";

// ── Query key factory ───────────────────────────────────────────────────────

export const documentKeys = {
  all: ["documents"] as const,
  lists: () => [...documentKeys.all, "list"] as const,
  list: (params: DocumentListParams) =>
    [...documentKeys.lists(), params] as const,
  details: () => [...documentKeys.all, "detail"] as const,
  detail: (id: string) => [...documentKeys.details(), id] as const,
};

export const approvalKeys = {
  all: ["approvals"] as const,
  pending: () => [...approvalKeys.all, "pending"] as const,
};

export const reviewKeys = {
  all: ["reviews"] as const,
  list: (documentId: string) => [...reviewKeys.all, documentId] as const,
};

// ── Document Queries ─────────────────────────────────────────────────────────

export function useDocumentList(params?: DocumentListParams) {
  return useQuery({
    queryKey: documentKeys.list(params ?? {}),
    queryFn: () => documentsApi.list(params),
  });
}

export function useDocument(id: string) {
  return useQuery({
    queryKey: documentKeys.detail(id),
    queryFn: () => documentsApi.getById(id),
    enabled: Boolean(id),
  });
}

export function usePendingApprovals() {
  return useQuery({
    queryKey: approvalKeys.pending(),
    queryFn: () => approvalsApi.pending(),
  });
}

// ── Document Mutations ──────────────────────────────────────────────────────

export function useUploadDocument() {
  const qc = useQueryClient();
  const [progress, setProgress] = useState(0);

  const mutation = useMutation({
    mutationFn: async ({
      file,
      documentType,
      title,
      description,
    }: {
      file: File;
      documentType?: DocumentType;
      title?: string;
      description?: string;
    }) => {
      return documentsApi.upload(
        file,
        documentType ?? "other",
        title,
        description,
        (pct) => setProgress(pct),
      );
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: documentKeys.lists() });
      setProgress(0);
    },
    onError: () => setProgress(0),
  });

  return { ...mutation, progress };
}

export function useNewVersion() {
  const qc = useQueryClient();
  const [progress, setProgress] = useState(0);

  return {
    ...useMutation({
      mutationFn: async ({
        documentId,
        file,
        title,
        description,
      }: {
        documentId: string;
        file: File;
        title?: string;
        description?: string;
      }) => {
        return documentsApi.newVersion(
          documentId,
          file,
          title,
          description,
          (pct) => setProgress(pct),
        );
      },
      onSuccess: (_, vars) => {
        qc.invalidateQueries({ queryKey: documentKeys.detail(vars.documentId) });
        qc.invalidateQueries({ queryKey: documentKeys.lists() });
        setProgress(0);
      },
      onError: () => setProgress(0),
    }),
    progress,
  };
}

export function useUpdateDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string;
      payload: DocumentUpdateRequest;
    }) => documentsApi.update(id, payload),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: documentKeys.detail(vars.id) });
      qc.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}

export function useSubmitDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => documentsApi.submitForReview(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: documentKeys.detail(id) });
      qc.invalidateQueries({ queryKey: documentKeys.lists() });
      qc.invalidateQueries({ queryKey: approvalKeys.pending() });
    },
  });
}

export function useApproveDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => documentsApi.approve(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: documentKeys.detail(id) });
      qc.invalidateQueries({ queryKey: documentKeys.lists() });
      qc.invalidateQueries({ queryKey: approvalKeys.pending() });
    },
  });
}

export function useRejectDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      documentsApi.reject(id, reason),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: documentKeys.detail(vars.id) });
      qc.invalidateQueries({ queryKey: documentKeys.lists() });
      qc.invalidateQueries({ queryKey: approvalKeys.pending() });
    },
  });
}

export function useExpireDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => documentsApi.expire(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: documentKeys.detail(id) });
      qc.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}

export function useArchiveDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => documentsApi.archive(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}

export function usePermanentDeleteDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => documentsApi.hardDelete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}

// ── Review Mutations ────────────────────────────────────────────────────────

export function useCreateReview(documentId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ grade, comment }: { grade: number; comment: string }) =>
      reviewsApi.create(documentId, grade, comment),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: reviewKeys.list(documentId) });
    },
  });
}

export function useReviewList(
  documentId: string,
  params?: { page?: number; page_size?: number },
) {
  return useQuery({
    queryKey: [...reviewKeys.list(documentId), params],
    queryFn: () => reviewsApi.list(documentId, params),
    enabled: Boolean(documentId),
  });
}
