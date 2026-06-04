"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { documentsApi, UploadDocumentPayload } from "@/lib/api/documents"
import { DocumentListParams } from "@/types/document"

export const documentKeys = {
  all:     ["documents"] as const,
  lists:   () => [...documentKeys.all, "list"] as const,
  list:    (p: DocumentListParams) => [...documentKeys.lists(), p] as const,
  detail:  (id: string) => [...documentKeys.all, "detail", id] as const,
  history: (groupId: string) => [...documentKeys.all, "history", groupId] as const,
}

export function useDocumentList(params?: DocumentListParams) {
  return useQuery({
    queryKey: documentKeys.list(params ?? {}),
    queryFn:  () => documentsApi.list(params),
  })
}

export function useDocument(id: string) {
  return useQuery({
    queryKey: documentKeys.detail(id),
    queryFn:  () => documentsApi.getById(id),
    enabled:  Boolean(id),
  })
}

export function useVersionHistory(groupId?: string) {
  return useQuery({
    queryKey: documentKeys.history(groupId ?? ""),
    queryFn:  () => documentsApi.getVersionHistory(groupId!),
    enabled:  Boolean(groupId),
  })
}

export function useUploadDocument() {
  const qc = useQueryClient()
  const [progress, setProgress] = useState(0)
  const [stage, setStage]       = useState<"idle" | "signing" | "uploading" | "confirming">("idle")

  const mutation = useMutation({
    mutationFn: async (payload: UploadDocumentPayload) => {
      setStage("signing")
      // documentsApi.upload xử lý 3 bước bên trong:
      // 1. Lấy Signed URL  2. PUT lên GCS  3. Confirm với backend
      const doc = await documentsApi.upload(payload, (pct) => {
        setStage("uploading")
        setProgress(pct)
      })
      setStage("confirming")
      return doc
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: documentKeys.lists() })
      setProgress(0)
      setStage("idle")
    },
    onError: () => setStage("idle"),
  })

  return { ...mutation, progress, stage }
}

export function useDeleteDocument() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => documentsApi.delete(id),
    onSuccess:  () => qc.invalidateQueries({ queryKey: documentKeys.lists() }),
  })
}

export function useCreateReview(documentId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ grade, comment }: { grade: number; comment: string }) =>
      documentsApi.createReview(documentId, grade, comment),
    onSuccess: () => qc.invalidateQueries({ queryKey: documentKeys.detail(documentId) }),
  })
}

export function useDownloadUrl(documentId: string, enabled = false) {
  return useQuery({
    queryKey: [...documentKeys.detail(documentId), "download-url"],
    queryFn:  () => documentsApi.getDownloadUrl(documentId),
    enabled,
    // Signed URL TTL 15 phút → stale sau 14 phút
    staleTime: 14 * 60 * 1000,
  })
}
